#include "controlserver.h"
#include "forecast.h"
#include "logging.h"
#include "storage.h"

#include <stdio.h> //TODO remove
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>

//   op    flagid    flag
// [ 4B ] [ 12 B ] [ 32 B ]

struct
{
	int32 operation;
	char flagId[12];
	char flag[32];
} request;

void wt_update_forecast_data()
{
	char rawData[WT_SAMPLES];
	int32 samples[WT_SAMPLES];

	memset(rawData, 0, sizeof(rawData));
	memset(samples, 0, sizeof(samples));

	int32 lastValuesAvailable;
	last_values *lastValues = wt_get_last_values(&lastValuesAvailable);

	for (int32 i = 0; i < lastValuesAvailable; i++)
		memcpy(rawData + i * WT_VALSAMPLES, (*lastValues)[i], WT_VALSAMPLES);

	wt_forecast_temp_prepare(rawData, samples);

	wt_forecast_temp_update(samples);
}

void wt_control_process_client(int32 serverSocket)
{
	struct sockaddr_in clientAddress;
	int32 clientLength = sizeof(clientAddress);

	int32 clientSocket = accept(serverSocket, (struct sockaddr *)&clientAddress, &clientLength);
	if (clientSocket < 0) 
	{
		wt_log_error("Failed to accept control client");
		return;
	}

	struct timeval tv;

	tv.tv_sec = 1;
	tv.tv_usec = 0;

	setsockopt(clientSocket, SOL_SOCKET, SO_RCVTIMEO, (char *)&tv, sizeof(tv));

	read(clientSocket, &request, sizeof(request));

	if (request.operation == 0)
	{
		wt_storage_get(request.flagId, request.flag);
		write(clientSocket, request.flag, sizeof(request.flag));
	}
	else if (request.operation == 1)
	{
		wt_storage_put(request.flagId, request.flag);
		wt_update_forecast_data();
	}

	close(clientSocket);
}