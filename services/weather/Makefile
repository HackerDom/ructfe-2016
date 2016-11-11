CC = gcc
CFLAGS = -std=c99 -m32 -O0 -fno-stack-protector  -fpie
LDFLAGS = -m32 -shared-libgcc -s -pie
DEPS =

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

WEATHER_OBJS = entrypoint.o server.o httpserver.o controlserver.o dispatcher.o storage.o forecast.o matrix.o types.o logging.o
weather: $(WEATHER_OBJS)
	gcc -o weather $(WEATHER_OBJS) $(LDFLAGS)

SIGNTOOL_OBJS = signtool.o forecast.o matrix.o types.o logging.o
signtool: $(SIGNTOOL_OBJS)
	gcc -o signtool $(SIGNTOOL_OBJS) $(LDFLAGS)

CHECKER_OBJS = checker.o forecast.o matrix.o types.o logging.o
checker: $(CHECKER_OBJS)
	gcc -o checker $(CHECKER_OBJS) $(LDFLAGS)

all: weather checker

clean:
	rm -f weather checker signtool *.o