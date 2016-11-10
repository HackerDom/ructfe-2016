#pragma once

#include "types.h"
#include "server.h"

int32 wt_start_control_server(uint32 address, int32 port);

void wt_control_process_client(const struct client *client);

void wt_update_forecast_data();