#include "dispatcher.h"
#include "server.h"
#include "httpserver.h"
#include "controlserver.h"
#include "logging.h"
#include "types.h"

#include <unistd.h>
#include <string.h>
#include <netinet/in.h>
#include <sys/poll.h>

#define PORT_HTTP 16780
#define PORT_CONTROL 16761

#define USR_FDS 1012
#define SRV_FDS 2

void add_client(struct pollfd *fds, struct client *clients, int32 *lastConnected, int32 newFd, int32 type)
{
	int32 fdIndex = (*lastConnected + 1) % USR_FDS;

	for (int32 i = 0; i < USR_FDS; i++)
	{
		int32 currentIndex = (fdIndex + i) % USR_FDS;

		if (fds[currentIndex].fd)
			continue;

		fdIndex = currentIndex;
		break;
	}

	if (fds[fdIndex].fd)
	{
		wt_log_warn("Ran out of connection slots, will disconnect someone.");

		wt_close_client(clients + fdIndex);
	}

	fds[fdIndex].fd = newFd;
	fds[fdIndex].events = POLLIN;

	clients[fdIndex].socket = newFd;
	clients[fdIndex].pollfd = fds + fdIndex;
	clients[fdIndex].type = type;

	*lastConnected = fdIndex;
}

int32 accept_client(int32 serverSocket)
{
	struct sockaddr_in clientAddress;
	int32 clientLength = sizeof(clientAddress);

	int32 clientSocket = accept(serverSocket, (struct sockaddr *)&clientAddress, &clientLength);
	if (clientSocket < 0) 
	{
		wt_log_error("Failed to accept client");
		return 0;
	}

	wt_make_nonblocking(clientSocket);

	return clientSocket;
}

void wt_run_dispatcher()
{
	wt_log_info("Starting HTTP server on prefix http://*:%d/", PORT_HTTP);

	int32 httpListener = wt_start_server(INADDR_ANY, PORT_HTTP);

	wt_log_info("Starting control server on port %d", PORT_CONTROL);

	int32 controlListener = wt_start_server(INADDR_ANY, PORT_CONTROL);

	struct pollfd fds[SRV_FDS + USR_FDS];

	memset(&fds, 0, sizeof(fds));

	fds[0].fd = controlListener;
	fds[0].events = POLLIN;

	fds[1].fd = httpListener;
	fds[1].events = POLLIN;

	struct pollfd *clientFds = fds + SRV_FDS;
	struct client clients[USR_FDS];

	int32 usedFds = SRV_FDS;
	int32 lastConnected = -1;

	while (true)
	{
		int32 result = poll(fds, usedFds, -1);

		if (result < 0)
			wt_error("poll() failed unexpectedly!");


		for (int32 i = 0; i < usedFds; i++)
		{
			if (fds[i].revents != POLLIN)
				continue;

			if (i < SRV_FDS)
			{
				int32 socket = accept_client(fds[i].fd);

				if (!socket)
					continue;

				add_client(clientFds, clients, &lastConnected, socket, i);

				if (usedFds < SRV_FDS + USR_FDS)
					usedFds++;

				continue;
			}

			int32 clientIndex = i - SRV_FDS;

			if (clients[clientIndex].type == 0)
				wt_control_process_client(clients + clientIndex);
			else
				wt_http_process_client(clients + clientIndex);
		}
	}
}