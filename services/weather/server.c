#include "server.h"

#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>

int32 wt_start_server(uint32 address, int32 port)
{
	int32 serverSocket = socket(AF_INET, SOCK_STREAM, 0);

	if (serverSocket < 0) 
		wt_error("Failed to open server socket");

	int32 reuse = 1;
	setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(int32));

	struct sockaddr_in serverAddress;

	bzero(&serverAddress, sizeof(serverAddress));

	serverAddress.sin_family = AF_INET;
	serverAddress.sin_addr.s_addr = htonl(address);
	serverAddress.sin_port = htons(port);

	if (bind(serverSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) < 0) 
		wt_error("Failed to bind server socket");

	int32 flags;
	if ((flags = fcntl(serverSocket, F_GETFL, 0)) < 0)
		wt_error("Failed to get socket flags");
	if (fcntl(serverSocket, F_SETFL, flags | O_NONBLOCK) < 0)
		wt_error("Failed to set socket flags");

	if (listen(serverSocket, 100) < 0)
		wt_error("Failed to listen on server socket");

	return serverSocket;
}