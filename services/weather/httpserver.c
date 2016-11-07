#include "httpserver.h"
#include "forecast.h"
#include "storage.h"
#include "logging.h"
#include "page.h"

#include <stdio.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <string.h>

#define BUFSIZE 1024

char inputBuffer[BUFSIZE];

char template[] = RESPONSE BODY;

char *weatherTypes[] = {
	"clear",
	"some clouds",
	"cloudy",
	"rain",
	"thunderstorm",
	"snow"
};

void get_forecast(const char *request, char *buffer)
{
	int32 forecast[WT_LAST_SAVED];

	wt_forecast_temp(forecast, WT_LAST_SAVED);

	wt_log_info("forecast ready");

	char typeRawData[WT_LAST_SAVED];
	char typeForecast[WT_LAST_SAVED];

	memset(typeRawData, 0, sizeof(typeRawData));
	memset(typeForecast, 0, sizeof(typeForecast));

	int32 lastValuesAvailable;
	last_values *lastValues = wt_get_last_values(&lastValuesAvailable);
	for (int32 i = 0; i < lastValuesAvailable; i++)
		typeRawData[i] = (*lastValues)[i][30];

	wt_log_info("typeRawData : %c", typeRawData[0]);
	wt_log_info("typeRawData : %c", typeRawData[1]);
	wt_log_info("typeRawData : %c", typeRawData[2]);
	wt_log_info("typeRawData : %c", typeRawData[3]);
	wt_log_info("typeRawData : %c", typeRawData[4]);
	wt_log_info("typeRawData : %c", typeRawData[5]);

	wt_log_info("lastValuesAvailable : %d", lastValuesAvailable);

	wt_forecast_type(typeRawData, forecast, WT_LAST_SAVED, typeForecast);

	char *requestString = strchr(request, '/');
	int32 requestLength = 0;
	if (requestString)
	{
		requestString++;
		while (!isspace(requestString[requestLength]))
			requestLength++; //TODO develop a vuln here
	}
	else
		requestString = "";

	uint64 signature = wt_sign(requestString, requestLength);

	sprintf(buffer, template,
		forecast[0], weatherTypes[typeForecast[0]],
		forecast[1], weatherTypes[typeForecast[1]],
		forecast[2], weatherTypes[typeForecast[2]],
		forecast[3], weatherTypes[typeForecast[3]],
		forecast[4], weatherTypes[typeForecast[4]],
		forecast[5], weatherTypes[typeForecast[5]],
		signature);
}

void wt_http_process_client(int32 serverSocket)
{
	struct sockaddr_in clientAddress;
	int32 clientLength = sizeof(clientAddress);

	int32 clientSocket = accept(serverSocket, (struct sockaddr *)&clientAddress, &clientLength);
	if (clientSocket < 0) 
	{
		wt_log_error("Failed to accept HTTP client");
		return;
	}

	struct timeval tv;

	tv.tv_sec = 1;
	tv.tv_usec = 0;

	setsockopt(clientSocket, SOL_SOCKET, SO_RCVTIMEO, (char *)&tv, sizeof(tv));

	read(clientSocket, inputBuffer, BUFSIZE);

	char response[BUFSIZE];
	get_forecast(inputBuffer, response);

	write(clientSocket, response, strlen(response));

	close(clientSocket);
}