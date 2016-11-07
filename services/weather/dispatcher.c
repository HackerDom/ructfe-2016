#include "dispatcher.h"
#include "server.h"
#include "httpserver.h"
#include "controlserver.h"
#include "logging.h"
#include "types.h"

#include <netinet/in.h>
#include <sys/select.h>

#define PORT_HTTP 16780
#define PORT_CONTROL 16761

void wt_run_dispatcher()
{
	wt_log_info("Starting HTTP server on prefix http://*:%d/", PORT_HTTP);

	int32 httpListener = wt_start_server(INADDR_ANY, PORT_HTTP);

	wt_log_info("Starting control server on port %d", PORT_CONTROL);

	int32 controlListener = wt_start_server(INADDR_ANY, PORT_CONTROL);

	fd_set fd_in;
	struct timeval tv;

	while (true)
	{
		FD_ZERO(&fd_in);

		FD_SET(httpListener, &fd_in);
		FD_SET(controlListener, &fd_in);

		tv.tv_sec = 10;
		tv.tv_usec = 0;

		int32 result = select(max(httpListener, controlListener) + 1, &fd_in, 0, 0, &tv);

		if (result == -1)
			wt_log_error("select() failed unexpectedly!");
		else if (result != 0)
		{
			if (FD_ISSET(controlListener, &fd_in))
				wt_control_process_client(controlListener);

			if (FD_ISSET(httpListener, &fd_in))
				wt_http_process_client(httpListener);
		}
	}
}