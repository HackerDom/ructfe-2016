#include "controlserver.h"
#include "forecast.h"
#include "logging.h"
#include "storage.h"

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

void wt_control_process_client(const struct client *client)
{
	memset(&request, 0, sizeof(request));
	
	if (read(client->socket, &request, sizeof(request)) == 0)
		return;

	if (request.operation == 0)
	{
		wt_storage_get(request.flagId, request.flag);
		write(client->socket, request.flag, sizeof(request.flag));
	}
	else if (request.operation == 1)
	{
		wt_storage_put(request.flagId, request.flag);
		wt_update_forecast_data();
	}

	wt_close_client(client);
}