local app = require('lapis').Application()
local redis = require 'redis'

local function is_significant(s)
	return s ~= nil and s ~= '';
end

local function get_user_and_password(context)
	local user = context.req.params_post.user
	local password = context.req.params_post.password
	if not is_significant(user) or not is_significant(password) then
		return
	end
	return user, password
end

app:before_filter(function(self)
	self.options.layout = false
end)

app:post('/register', function(self)
	local client = redis:client()
	local user, password = get_user_and_password(self)

	if not user then
		return {status = 400, json = {'user and password must be present'}}
	end

	if client:user_exists(user) then
		return {status = 400, json = {'username already exists'}}
	end

	client:create_user(user, password)
	if not client:user_exists(user, password) then
		return {status = 400, json = {'username already exists'}}
	end

	self.session.user = user
	self.session.date = os.time()
end)

app:post('/login', function(self)
	local client = redis:client()
	local user, password = get_user_and_password(self)

	if not user then
		return {status = 400, json = {'user and password must be present'}}
	end

	if client:user_exists(user, password) then
		self.session.user = user
		self.session.date = os.time()
	else
		return {status = 400, json = {'wrong username or password'}}
	end
end)

app:get('/logout', function(self)
	self.session.user = nil
end)

app:post('/upload', function(self)
	local client = redis:client()
	local file = self.req.params_post.file
	local is_public = self.req.params_post.is_public
	local user = self.session.user

	if not user then
		return {status = 401, json = {'need to login'}}
	end
	if not file then
		return {status = 400, json = {'file required'}}
	end

	local data = file.content
	if string.len(data) > 65536 then
		return {status = 400, json = {'file too large'}}
	end

	is_public = is_public and true or false
	local url = client:create_file(user, data, is_public, function(filename) return self:url_for('download', {id = filename}) end)

	if url then
		return {json = {url}}
	else
		return {status = 500, json = {'error while process file'}}
	end
end)

app:get('download', '/file/:id', function(self)
	local client = redis:client()
	local data = client:get_file(self.params.id)
	if data == nil then
		return {status = 404}
	else
		self:write(data, {content_type = 'text/plain'})
	end
end)

app:get('/all/:id', function(self)
end)

return app
