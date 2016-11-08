local server = require 'resty.websocket.server'
local redis = require 'redis'
local json = require 'json'

local module = {}

local function send_post(client, socket, post)
	local data = client:get_post_info(post)
	if not data then
		return true
	end
	local bytes, err = socket:send_text(json:encode(data))
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

	for post in client:get_public_posts() do
		if not send_post(client, socket, post) then
			break
		end
	end

	for post in listener:get_news() do
		if not send_post(client, socket, post) then
			break
		end
	end

	listener:close()
	socket:send_close()
end

return module
