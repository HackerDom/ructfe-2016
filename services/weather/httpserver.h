#pragma once

#include "types.h"

int32 wt_start_http_server(uint32 address, int32 port);

void wt_http_process_client(int32 serverSocket);