local ffi = require 'ffi'

ffi.cdef [[
	typedef struct {
		unsigned long long state;
		unsigned value;
	} result_t;

	result_t next(unsigned long long state);
	unsigned long long init();
]]

local crand = ffi.load '/etc/nginx/rand.so'

local module = {}

function module.init()
	return tonumber(crand.init());
end

setmetatable(module, {
	__call = function(_, value)
		value = tonumber(value)
		local res = crand.next(value)
		return tonumber(res.state), tonumber(res.value)
	end
})

return module
