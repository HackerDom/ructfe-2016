local redis = require 'resty.redis'
local config = require('lapis.config').get()
local rand = require 'rand'
local sha1 = require 'sha1'

require 'utils'

local module = {}

local function get_userid(username)
	return 'user:' .. username
end

local function get_fileid(filename)
	return 'file:' .. filename
end

local function hash(username, password)
	return sha1(username .. config.secret .. password)
end

local function user_exists(self, username, password)
	local userid = get_userid(username)
	if not password then
		return self.client:exists(userid) ~= 0
	else
		return self.client:hget(userid, 'password') == hash(username, password)
	end
end

local function create_user(self, username, password)
	self.client:hmset(get_userid(username), 'password', hash(username, password), 'state', rand.init())
end

local function create_file(self, username, data, public, get_url)
	local userid = get_userid(username)

	local state, value = self.client:hget(userid, 'state')
	state, value = rand(state)
	self.client:hset(userid, 'state', state)

	local filename = sha1(value .. '@' .. username)
	local expired = os.time() + config.ttl
	local url = get_url(filename)
	local fileid = get_fileid(filename)

	self.client:multi()
	self.client:hmset(fileid, 'owner', username, 'public', public, 'expired', expired, 'url', url, 'data', data)
	self.client:expire(fileid, config.ttl)
	if public then
		self.client:zadd('publics', expired, filename)
		self.client:publish('publics', filename)
	end

	local ok, err = self.client:exec()
	if not ok then
		error('fail exec: ' .. err)
	end

	return url
end

local function get_file(self, filename)
	local data = self.client:hget(get_fileid(filename), 'data')
	if data ~= ngx.null then
		return data
	end
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

local function get_public_files(self)
	return get_all(self.client, 'publics')
end

local function get_file_info(self, filename)
	local id = get_fileid(filename)
	local url, owner, expired = unpack(self.client:hmget(id, 'url', 'owner', 'expired'))
	if url ~= ngx.null then
		return {url = url, owner = owner, ttl = expired - os.time()}
	end
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
		user_exists = user_exists,
		create_user = create_user,
		create_file = create_file,
		get_file = get_file,
		get_public_files = get_public_files,
		get_file_info = get_file_info
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
	self.client:unsubscribe('publics')
end

function module.listener()
	local client = create_client()
	local res, err = client:subscribe('publics')

	if not res then
		error('failed for subscribe: ' .. err)
	end
	return {
		client = client,
		get_news = get_all_replaies,
		close = unsubscribe
	}
end

return module
