#include "server.h"
#include "forecast.h"

#include <unistd.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>

char *weatherTypes[] = {
	"clear",
	"some clouds",
	"cloudy",
	"rain",
	"thunderstorm",
	"snow"
};

void wt_fill_template(const char *request, char *buffer, const char *template)
{
	int32 forecast[WT_LAST_SAVED];

	wt_forecast_temp(forecast, WT_LAST_SAVED);

	char typeRawData[WT_LAST_SAVED];
	char typeForecast[WT_LAST_SAVED];

	memset(typeRawData, 0, sizeof(typeRawData));
	memset(typeForecast, 0, sizeof(typeForecast));

	int32 lastValuesAvailable;
	last_values *lastValues = wt_get_last_values(&lastValuesAvailable);
	for (int32 i = 0; i < lastValuesAvailable; i++)
		typeRawData[i] = (*lastValues)[i][30];

	wt_forecast_type(typeRawData, forecast, WT_LAST_SAVED, typeForecast);

	char *requestString = strchr(request, '/');
	int32 requestLength = 0;
	if (requestString)
	{
		requestString++;
		while (!isspace(requestString[requestLength]))
			requestLength++;
	}
	else
		requestString = "";

	uint64 signature = wt_sign(requestString, requestLength);

	if (!template[0])
		wt_error("Template is not initialized");

	sprintf(buffer, template,
		forecast[0], weatherTypes[typeForecast[0]],
		forecast[1], weatherTypes[typeForecast[1]],
		forecast[2], weatherTypes[typeForecast[2]],
		forecast[3], weatherTypes[typeForecast[3]],
		forecast[4], weatherTypes[typeForecast[4]],
		forecast[5], weatherTypes[typeForecast[5]],
		signature);
}

void wt_make_nonblocking(int32 socket)
{
	int32 flags;
	if ((flags = fcntl(socket, F_GETFL, 0)) < 0)
		wt_error("Failed to get socket flags");
	if (fcntl(socket, F_SETFL, flags | O_NONBLOCK) < 0)
		wt_error("Failed to set socket flags");
}

void wt_close_client(const struct client *client)
{
	close(client->socket);
	memset(client->pollfd, 0, sizeof(struct pollfd));
}

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

	wt_make_nonblocking(serverSocket);

	if (listen(serverSocket, 100) < 0)
		wt_error("Failed to listen on server socket");

	return serverSocket;
}