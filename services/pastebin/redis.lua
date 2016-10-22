local redis = require 'resty.redis'
local config = require('lapis.config').get()

local module = {}

function module.client(self)
	local client = redis:new()
	local ok, err = client:connect(config.redis.host, config.redis.port)
	if not ok then
		error('fail to connect: ' .. err)
	end
	return client
end

return module
