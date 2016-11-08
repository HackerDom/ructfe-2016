local json = require 'cjson'

local module = {json = json.new()}

function module.encode(self, t)
	return self.json.encode(t)
end

function module.decode(self, str)
	local ok, err = pcall(self.json.decode(str))
	if not ok then
		return nil
	end	
	return fix(t)
end

local function fix(t)
	if type(t) == 'table' then
		local result = {}
		for pos, val in pairs(t) do
			result[pos] = fix(value)
		end
		return result
	elseif t == json.null then
		return nil
	else
		return t	
	end
end

return module