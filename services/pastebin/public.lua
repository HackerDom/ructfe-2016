require 'utils'

local server = require 'resty.websocket.server'
local redis = require 'redis'
local json = require 'cjson'

local module = {}

local function get_all_elements(client, field)
	local cursor, elements, i = 0
	local function get_next()
		cursor, elements = unpack(client:zscan('publics', cursor))
		i = 0
	end
	get_next()
	return function() 
		while i == #elements do
			if cursor == 0 then
				return
			else
				get_next()
			end
		end
		i = i + 1
		return elements[i][1]
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
	
	local client = redis:client()
	client:zremrangebyscore('publics', 0, os.time())
	
	for file in get_all_elements(client, 'publics') do
	    local bytes, err = socket:send_text(json.encode(file))
		if not bytes then
			return
		end
	end
end

return module
