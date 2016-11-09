local redis = require 'resty.redis'
local config = require('lapis.config').get()
local rand = require 'rand'
local md5 = require 'md5'
local json = require 'json'

require 'utils'

local module = {}

local function get_userid(username)
	return 'user:' .. username
end

local function get_postid(postname)
	return 'post:' .. postname
end

local function get_listid(username)
	return 'posts:user:' .. username
end

module.get_listid = get_listid

local function hash(username, password)
	return md5.sumhexa(username .. config.secret .. password)
end

local function create_user(self, username, password, skills_list)
	local userid = get_userid(username)
	local passhash = hash(username, password)
	if self.client:hsetnx(userid, 'password', passhash) == 1 then
		local skills = json:encode(skills_list)
		self.client:hmset(userid, 'state', rand.init(), 'skills', skills)
		return true
	end
	return self.client:hget(userid, 'password') == passhash
end

local function create_post(self, username, title, body, public, requirement, sign, get_url)
	local userid = get_userid(username)

	local state, value = self.client:hget(userid, 'state')
	state, value = rand(state)
	self.client:hset(userid, 'state', state)

	local secret = value .. '@' .. username
	local postname = md5.sumhexa(secret)
	local show_time = os.time() + config.show_time
	local expired = os.time() + config.ttl
	local url = get_url(postname)
	local postid = get_postid(postname)
	local listid = get_listid(username)

	self.client:multi()
	self.client:hmset(postid, 'owner', username, 'public', public, 'url', url, 'title', title, 'body', body, 'requirement', requirement, 'sign', sign)
	self.client:expire(postid, config.ttl)
	self.client:zadd(listid, expired, postname)
	if public then
		self.client:zadd('publics', show_time, postname)
		self.client:publish('publics', postname)
	end
	self.client:publish(listid, postname)

	local ok, err = self.client:exec()
	if not ok then
		error('fail exec: ' .. err)
	end

	return url
end

local function get_post(self, postname, user)
	local skills

	local title, body, owner, requirement, sign = unpack(self.client:hmget(get_postid(postname), 'title', 'body', 'owner', 'requirement', 'sign'))
	if title == ngx.null or body == ngx.null then
		return nil
	end

	local post = {title = title, body = body, owner = owner, sign = sign}

	if user == owner then
		return post
	end

	if not user then
		skills = {''}
	else
		local userid = get_userid(user)
		skills = self.client:hget(userid, 'skills')
		skills = json:decode(skills)
	end

	for k, skill in ipairs(skills) do
		if skill == requirement then
			return post
		end
		if skill == '' then
			return nil
		end	
	end

	return post
end

local function get_all(client, key)
	client:zremrangebyscore(key, 0, os.time())

	local cursor, elements, i = 0
	local function get_next()
		cursor, elements = unpack(client:zscan(key, cursor))
		i = -1
	end
	get_next()

	return function()
		while i + 1 == #elements do
			if cursor == '0' then
				return
			else
				get_next()
			end
		end
		i = i + 2
		return elements[i]
	end
end

local function get_list(self, list)
	return get_all(self.client, list)
end

local function get_post_info(self, postname)
	local id = get_postid(postname)
	local url, owner, title = unpack(self.client:hmget(id, 'url', 'owner', 'title'))
	if url ~= ngx.null then
		return {url = url, owner = owner, title = title}
	end
end

local function get_posts_for_user(self, user)
	local listid = get_listid(user)
	return get_all(self.client, listid)
end

local function create_client()
	local client = redis:new()
	local ok, err = client:connect(config.redis.host, config.redis.port)
	if not ok then
		error('fail to connect: ' .. err)
	end
	return client
end

function module.client()
	return {
		client = create_client(),
		create_user = create_user,
		update_skills = update_skills,
		create_post = create_post,
		get_post = get_post,
		get_list = get_list,
		get_post_info = get_post_info,
		get_posts_for_user = get_posts_for_user
	}
end

local function get_all_replaies(self)
	return function()
		local res, err = self.client:read_reply()
		if res then
			return res[3]
		end
	end
end

local function unsubscribe(self)
	self.client:unsubscribe(self.list)
end

function module.listener(list)
	local client = create_client()
	local res, err = client:subscribe(list)

	if not res then
		error('failed for subscribe: ' .. err)
	end
	return {
		client = client,
		list = list,
		get_news = get_all_replaies,
		close = unsubscribe
	}
end

return module
