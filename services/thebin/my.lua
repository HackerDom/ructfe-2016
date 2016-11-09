local ws = require 'ws'
local util = require 'lapis.util'
local session_util = require 'lapis.session'
local redis = require 'redis'

local module = {}

function module.process()
	local cookies = util.parse_cookie_string(ngx.req.get_headers().cookie)
	local session = session_util.get_session({cookies = cookies})

	if not session then
		return
	end

	local user = session.user

	if not user then
		return
	end

	ws.process(redis.get_listid(user))
end

return module