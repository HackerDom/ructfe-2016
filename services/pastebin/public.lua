local server = require 'resty.websocket.server'
local redis = require 'redis'
local json = require 'cjson'

local module = {}

local function get_all_elements(client, field)
	local cursor, elements, i = 0
	local function get_next()
		cursor, elements = unpack(client:zscan('publics', cursor))
		i = -1
	end
	get_next()
	return function() 
		while i + 1 == #elements do
			if cursor == "0" then
				return
			else
				get_next()
			end
		end
		i = i + 2
		return elements[i]
	end
end

local function get_all_replaies(client)
	return function()
		local res, err = client:read_reply()
		if res then
			return res[3]
		end
	end
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

	local listener = redis:client()

	local res, err = listener:subscribe('publics')
	if not res then
		ngx.log(ngx.ERR, 'failed for subscribe: ', err)
		return ngx.exit(500)
	end

	local client = redis:client()
	client:zremrangebyscore('publics', 0, os.time())

	for file in get_all_elements(client, 'publics') do
	    local bytes, err = socket:send_text(json.encode(file))
		if not bytes then
			break
		end
	end

	for file in get_all_replaies(listener) do
		local bytes, err = socket:send_text(json.encode(err[3]))
		if not bytes then
			break
		end
	end

	listener:unsubscribe('publics')
	socket:send_close()
end

return module
