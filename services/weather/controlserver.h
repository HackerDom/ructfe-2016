#pragma once

#include "types.h"

int32 wt_start_control_server(uint32 address, int32 port);

void wt_control_process_client(int32 serverSocket);

void wt_update_forecast_data();