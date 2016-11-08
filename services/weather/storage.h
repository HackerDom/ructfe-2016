#pragma once

#include "types.h"

#define WT_LAST_SAVED 6

typedef char *last_values[WT_LAST_SAVED];

void wt_init_storage(const char *filename);

void wt_storage_get(const char *key, char *value);

void wt_storage_put(const char *key, const char *value);

last_values *wt_get_last_values(int32 *available);