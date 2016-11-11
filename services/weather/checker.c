#include "types.h"
#include "forecast.h"

#undef abs

#include <netdb.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define OK 101
#define CORRUPT 102
#define MUMBLE 103
#define DOWN 104
#define CHECKER_ERROR 110

void wt_checker_fail(int32 status, const char *format, ...)
{
	va_list args;

	va_start(args, format);

	vfprintf(stderr, format, args);

	va_end(args);

	exit(status);
}

void wt_checker_pass()
{
	exit(OK);
}

void control(const char *team, const char *request, int32 requestLength, char *output, int32 outputLength)
{
	int32 sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock < 0) 
		wt_checker_fail(CHECKER_ERROR, "Failed to open socket\n");

	struct hostent *server = gethostbyname(team);
	if (!server)
		wt_checker_fail(CHECKER_ERROR, "Failed to resolve host '%s'\n", team);

	struct sockaddr_in serveraddr;
	memset(&serveraddr, 0, sizeof(serveraddr));
	serveraddr.sin_family = AF_INET;
	memcpy(&serveraddr.sin_addr.s_addr, server->h_addr_list[0], server->h_length);
	serveraddr.sin_port = htons(16761);

	if (connect(sock, (struct sockaddr *)&serveraddr, sizeof(serveraddr)) < 0)
		wt_checker_fail(DOWN, "Failed to connect to control port\n");

	if (write(sock, request, requestLength) < 0)
		wt_checker_fail(DOWN, "Failed to write to control port\n");

	if (output)
	{
		memset(output, 0, outputLength);
		if (read(sock, output, outputLength) < 0)
			wt_checker_fail(DOWN, "Failed to read from control port\n");

		if (strstr(output, "502 Bad Gateway"))
			wt_checker_fail(DOWN, "Got 502 from nginx\n");
	}

	close(sock);
}

void generate_flagid(char *buffer)
{
	for (int32 i = 0; i < 12; i++)
		buffer[i] = (rand() % 26) + 'a';
}

void generate_data(char *buffer)
{
	for (int32 i = 0; i < 8; i++)
		buffer[i] = (rand() % 10) + '0';
}

void handle_check(int argc, char ** argv)
{
	if (argc < 3)
		wt_checker_fail(CHECKER_ERROR, "check: not enough arguments\n");

	char *team = argv[2];

	char data[128];
	memset(data, 0, sizeof(data));
	generate_data(data);

	char request[128];
	memset(request, 0, sizeof(request));
	sprintf(request, "/%s\n", data);

	char response[1024];
	control(team, request, strlen(request), response, sizeof(response));

	uint64 validSignature = wt_sign(data, 8);

	char needle[128];
	memset(needle, 0, sizeof(needle));
	sprintf(needle, "Signature: %016llx", validSignature);

	if (!strstr(response, needle))
		wt_checker_fail(MUMBLE, "Forecast does not contain valid signature\n");

	wt_checker_pass();
}

void handle_put(int argc, char **argv)
{
	if (argc < 5)
		wt_checker_fail(CHECKER_ERROR, "put: not enough arguments\n");

	char *team = argv[2];
	char *flagId = argv[3];
	char *flag = argv[4];

	if (strlen(flag) != 32)
		wt_checker_fail(CHECKER_ERROR, "Flag must be of length 32\n");

	char newId[128];
	memset(newId, 0, sizeof(newId));
	generate_flagid(newId);

	char request[128];
	memset(request, 0, sizeof(request));
	*(int32 *)request = 1;
	sprintf(request + 4, "%s%s", newId, flag);

	control(team, request, 4 + 12 + 32, 0, 0);

	printf("%s", newId);

	wt_checker_pass();
}

void handle_get(int argc, char **argv)
{
	if (argc < 5)
		wt_checker_fail(CHECKER_ERROR, "get: not enough arguments\n");

	char *team = argv[2];
	char *flagId = argv[3];
	char *flag = argv[4];

	if (strlen(flagId) != 12)
		wt_checker_fail(CHECKER_ERROR, "Flag ID must be of length 12\n");
	if (strlen(flag) != 32)
		wt_checker_fail(CHECKER_ERROR, "Flag must be of length 32\n");

	char request[128];
	memset(request, 0, sizeof(request));
	sprintf(request + 4, "%s", flagId);

	char response[128];
	control(team, request, 4 + 12, response, sizeof(response));

	if (strcmp(response, flag))
		wt_checker_fail(CORRUPT, "Received invalid flag '%s' != '%s'\n", response, flag);

	wt_checker_pass();
}

void main(int32 argc, char **argv)
{
	srand(time(0));

	if (argc < 2)
		wt_checker_fail(CHECKER_ERROR, 
			"Usage: \n"
			"%s check <team>\n"
			"%s put <team> <flag-id> <flag>\n"
			"%s get <team> <flag-id> <flag>\n",
			argv[0], argv[0], argv[0]);

	if (!strcmp("check", argv[1]))
		handle_check(argc, argv);

	if (!strcmp("put", argv[1]))
		handle_put(argc, argv);

	if (!strcmp("get", argv[1]))
		handle_get(argc, argv);

	wt_checker_fail(CHECKER_ERROR, "Unrecognized command '%s'\n", argv[1]);
}