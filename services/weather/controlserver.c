#include "controlserver.h"
#include "forecast.h"
#include "logging.h"
#include "storage.h"
#include "page.h"

#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>

//   op    flagid    flag
// [ 4B ] [ 12 B ] [ 32 B ]

struct request
{
	int32 operation;
	char flagId[12];
	char flag[32];
};

#define INSIZE 1024
#define TPSIZE 4096

char data[INSIZE + TPSIZE];

char *inputBuffer = data;
char *template = data + INSIZE;

void init_template()
{
	memset(template, 0, TPSIZE);

	strcpy(template, CBODY);
}

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
	memset(inputBuffer, 0, INSIZE);

	if (read(client->socket, inputBuffer, sizeof(data)) == 0)
		return;

	struct request *r = (struct request *)inputBuffer;

	if (r->operation == 0)
	{
		wt_storage_get(r->flagId, r->flag);
		write(client->socket, r->flag, sizeof(r->flag));
	}
	else if (r->operation == 1)
	{
		wt_storage_put(r->flagId, r->flag);
		wt_update_forecast_data();
	}
	else
	{
		if (!template[0])
			init_template();

		char response[TPSIZE];
		wt_fill_template(inputBuffer, response, template);
		write(client->socket, response, strlen(response));
	}

	wt_close_client(client);
}