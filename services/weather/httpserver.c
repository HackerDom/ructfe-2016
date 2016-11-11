#include "httpserver.h"
#include "page.h"

#include <unistd.h>
#include <string.h>

#define TPSIZE 4096

char inputBufferHttp[1024];
char templateHttp[] = RESPONSE BODY;

void wt_http_process_client(const struct client *client)
{
	if (read(client->socket, inputBufferHttp, sizeof(inputBufferHttp)) == 0)
		return;

	char response[TPSIZE];
	wt_fill_template(inputBufferHttp, response, templateHttp);

	write(client->socket, response, strlen(response));

	wt_close_client(client);
}