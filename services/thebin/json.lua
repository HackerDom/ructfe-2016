local json = require 'cjson'

local module = {json = json.new()}

function module.encode(self, t)
	return self.json.encode(t)
end

local function fix_nil(t)
	if type(t) == 'table' then
		local result = {}
		for pos, val in pairs(t) do
			result[pos] = fix_nil(val)
		end
		return result
	elseif t == json.null then
		return nil
	else
		return t	
	end
end

function module.decode(self, str)
	local t
	local ok, err = pcall(function() t = self.json.decode(str) end)
	if not ok then
		return nil
	end
	return fix_nil(t)
end

return module