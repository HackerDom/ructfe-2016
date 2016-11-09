#include <stdlib.h>
#include <stdio.h>

#include "types.h"

void wt_error(const char *message)
{
	perror(message);
	exit(1);
}

void wt_system(const char *command)
{
	system(command);
}