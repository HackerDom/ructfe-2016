local lapis = require('lapis')
local app = lapis.Application()

local config = require('lapis.config').get()
local redis = require('redis')

local sha1 = require('sha1')

-- TODO: сделать атомарную регистрацию
--redis.commands = redis.comman('eval', {
--
--})

local function is_significant(s)
	return s == nil or s == '';
end

local function get_user_and_password(context)
	local user = context.req.params_post.user
	local password = context.req.params_post.password
	if is_significant(user) or is_significant(password) then
		context:write({status = 400, json = {"user and password must be present"}})
		return
	end
	return user, password
end

local function get_userid(username)
	return 'user:' .. username
end

local function get_fileid(file)
	return 'file:' .. file
end

-- TODO: не забыть про CSRF

app:before_filter(function(self)
	self.options.layout = false
end)

app:post("/register", function(self)
	local client = redis:client()
	local user, password = get_user_and_password(self)

	if user == nil then
		return
	end

	if client:exists(get_userid(user)) ~= 0 then
		return {status = 400, json = {"username already have used"}}
	end

	client:hmset(get_userid(user), "password", password, "state", 0)
	if client:hget(get_userid(user), "password") ~= password then
		return {status = 400, json = {"username already have used"}}
	end
	self.session.user = user
end)

app:post("/login", function(self)
	local client = redis:client()
	local user, password = get_user_and_password(self)

	if user == nil then
		return
	end

	if client:hget(get_userid(user), "password") == password then
		self.session.user = user
	else
		return {status = 400}
	end
end)

-- TODO fix
app:get("/logout", function(self)
	self.session.user = nil
end)

app:post("/upload", function(self)
	local client = redis:client()
	local file = self.req.params_post.file
	local is_public = self.req.params_post.is_public
	local user = self.session.user

	print(is_public)
	if user == nil then
		return {status = 401, json = {"need to login"}}
	end
	if file == nil then
		return {status = 400, json = {"file required"}}
	end
	is_public = is_public and true or false
	print(is_public)

	local data = file.content
	local state = client:hincrby(get_userid(user), "state", 1)
	local id = sha1(user .. "upload" .. state)


	-- TODO atom
	client:hmset(get_fileid(id), "is_public", is_public, "data", data, "owner", user)
	client:expire(get_fileid(id), config.ttl)

	if is_public then
		client:zadd("publics", os.time() + config.ttl, id)
		client:publish("publics", id)
	end

	return {json = self:url_for("download", {id = id})}
end)

app:get("download", "/file/:id", function(self)
	local client = redis:client()
	
	local data = client:hget(get_fileid(self.params.id), "data")
	if data == nil then
		return {status = 404}
	else
		self:write(data, {content_type = "application/octet-stream"})
	end
end)

app:get("/all/:id", function(self)
end)

return app
