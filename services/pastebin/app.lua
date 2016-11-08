local app = require('lapis').Application()
local redis = require 'redis'

require 'utils'

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

app:post('/login', function(self)
	local client = redis:client()
	local user, password = get_user_and_password(self)

	if not user then
		return {status = 400, json = {'user and password must be present'}}
	end

	if client:user_exists(user, password) then
		self.session.user = user
	else
		return {status = 400, json = {'wrong username or password'}}
	end
end)

app:post('/logout', function(self)
	self.session.user = nil
end)

app:post('/publish', function(self)
	local client = redis:client()
	local title = self.req.params_post.title
	local body = self.req.params_post.body
	local is_public = self.req.params_post.is_public
	local sign = self.req.params_post.sign
	local user = self.session.user

	if not user then
		return {status = 401, json = {'need to login'}}
	end
	if not title then
		return {status = 400, json = {'title required'}}
	end

	if string.len(title) > 1024 then
		return {status = 400, json = {'title too large'}}
	end

	if string.len(body) > 65536 then
		return {status = 400, json = {'body too large'}}
	end

	if sign and string.len(sign) > 65536 then
		return {status = 400, json = {'sign too large'}}
	end

	if not sign then
		sign = ''
	end

	is_public = is_public == 'on' and true or false
	local url = client:create_post(user, title, body, is_public, sign, function(id) return self:url_for('view', {id = id}) end)

	if url then
		return {json = {url}}
	else
		return {status = 500, json = {'error while process notice'}}
	end
end)

app:get('view', '/post/:id', function(self)
	local client = redis:client()
	local data = client:get_post(self.params.id)
	if not data then
		return {status = 404}
	else
		return {json = data}
	end
end)

app:post('/all', function(self)
	local client = redis:client()
	local posts = {}
	local user = self.session.user
	if not user then
		return {status = 401, json = {'need to login'}}
	end	
	for post in client:get_posts_for_user(user) do
		local info = client:get_post_info(post)
		if info then
			table.insert(posts, info)
		end	
	end
	return {json = posts}
end)

app:post('/reply', function(self)
	local client = redis:client()
end)

return app
