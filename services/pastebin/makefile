.PHONY: all

all: rand.so lapis sha1

lapis:
	luarocks install lapis

sha1:
	luarocks install sha1

rand.so: rand.c
	gcc -shared -fPIC -Wall -Wextra -O3 rand.c -o rand.so
