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

#define TPSIZE 4096

char data[1024 + 4096];

char *inputBuffer = data;
char *template = data + 1024;

char *weatherTypes[] = {
	"clear",
	"some clouds",
	"cloudy",
	"rain",
	"thunderstorm",
	"snow"
};

void init_template()
{
	memset(template, 0, TPSIZE);

	strcat(template, RESPONSE);
	strcat(template, BODY);
}

void get_forecast(const char *request, char *buffer)
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
		init_template();

	sprintf(buffer, template,
		forecast[0], weatherTypes[typeForecast[0]],
		forecast[1], weatherTypes[typeForecast[1]],
		forecast[2], weatherTypes[typeForecast[2]],
		forecast[3], weatherTypes[typeForecast[3]],
		forecast[4], weatherTypes[typeForecast[4]],
		forecast[5], weatherTypes[typeForecast[5]],
		signature);
}

void wt_http_process_client(const struct client *client)
{
	if (read(client->socket, inputBuffer, sizeof(data)) == 0)
		return;

	char response[TPSIZE];
	get_forecast(inputBuffer, response);

	write(client->socket, response, strlen(response));

	wt_close_client(client);
}