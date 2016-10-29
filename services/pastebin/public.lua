local server = require 'resty.websocket.server'
local redis = require 'redis'
local json = require 'cjson'

local module = {}

local function send_file(client, socket, file)
	local data = client:get_file_info(file)
	if not data then
		return true
	end
	local bytes, err = socket:send_text(json.encode(data))
	return bytes and true or false 
end

function module.process()
	local socket, err = server:new {
	    timeout = 60000,
	    max_payload_len = 65535
	}

	if not socket then
	    ngx.log(ngx.ERR, 'failed for new websocket: ', err)
	    return ngx.exit(444)
	end

	local listener = redis:listener()
	local client = redis:client()

	for file in client:get_public_files() do
		if not send_file(client, socket, file) then
			break
		end
	end

	for file in listener:get_news() do
		if not send_file(client, socket, file) then
			break
		end
	end

	listener:close()
	socket:send_close()
end

return module
