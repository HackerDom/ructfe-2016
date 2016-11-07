#include "forecast.h"
#include "types.h"
#include "logging.h"

#include <string.h>
#include <stdio.h>

int32 main(int argc, char **argv)
{
	if (argc != 2)
	{
		printf("Usage: %s <data-to-sign>\n", argv[0]);
		return 0;
	}

	printf("%016llx\n", wt_sign(argv[1], strlen(argv[1])));
}
