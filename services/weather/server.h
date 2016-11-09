#pragma once

#include "types.h"

#include <sys/poll.h>


struct client
{
	int32 socket;
	struct pollfd *pollfd;
	int32 type;
};

void wt_close_client(const struct client *client);

void wt_make_nonblocking(int32 socket);

int32 wt_start_server(uint32 address, int32 port);