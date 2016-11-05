#!/bin/sh

config=/etc/nginx/config.lua

if test ! -e $config; then
        secret=`head -c 1024 /dev/urandom | sha512sum`;
cat > $config <<- END
local config = require("lapis.config").config

config("development", {
	session_name = "auth",
	secret = "$secret",
	redis = {
		host = "127.0.0.1",
		port = "6379"
	},
	ttl = 1200,
	show_time = 10,
})
END
fi
