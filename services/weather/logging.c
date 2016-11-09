#include "logging.h"
#include "types.h"

#include <stdio.h>
#include <stdarg.h>
#include <time.h>

#define LOG_BUFFER_SIZE 256

int32 echoToConsole = 1;

FILE *logStream;

void wt_init_logging(const char *filename)
{
	logStream = fopen(filename, "a");

	if (!logStream)
		wt_error("Failed to open log file");
}

void log_message(const char *type, const char *message)
{
	char buffer[26];
	struct tm* tm_info;
	time_t timer;

	if (!logStream)
		return;

	time(&timer);
	tm_info = localtime(&timer);

	strftime(buffer, 26, "%Y-%m-%d %H:%M:%S", tm_info);

	fprintf(logStream, "%s [%s] %s\n", buffer, type, message);
	fflush(logStream);

	if (echoToConsole)
		printf("%s [%s] %s\n", buffer, type, message);
}

void wt_log_info(const char *format, ...)
{
	char buffer[LOG_BUFFER_SIZE];

	va_list args;

	va_start(args, format);

	vsprintf(buffer, format, args);

	va_end(args);

	log_message("INFO", buffer);
}

void wt_log_warn(const char *format, ...)
{
	char buffer[LOG_BUFFER_SIZE];

	va_list args;

	va_start(args, format);

	vsprintf(buffer, format, args);

	va_end(args);

	log_message("WARN", buffer);
}

void wt_log_error(const char *format, ...)
{
	char buffer[LOG_BUFFER_SIZE];

	va_list args;

	va_start(args, format);

	vsprintf(buffer, format, args);

	va_end(args);

	log_message("ERROR", buffer);
}