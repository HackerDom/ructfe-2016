local config = require("lapis.config").config

config("development", {
	session_name = "auth",
	secret = "qqq",
	redis = {
		host = "127.0.0.1",
		port = "6379"
	},
	ttl = 1200,
	show_time = 10,
})
