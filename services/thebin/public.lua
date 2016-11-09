local ws = require 'ws'

local module = {}

function module.process()
	ws.process('publics')
end

return module
