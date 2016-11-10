#pragma once

#include "types.h"
#include "storage.h"

#define WT_CLEAR 0
#define WT_SOME_CLOUDS 1
#define WT_CLOUDY 2
#define WT_RAIN 3
#define WT_THUNDERSTORM 4
#define WT_SNOW 5

#define WT_VALSAMPLES 2
#define WT_SAMPLES (WT_VALSAMPLES * WT_LAST_SAVED)
#define WT_POLY_POWER 3

void wt_forecast_temp_prepare(const char *rawSamples, int32 *samples);

void wt_forecast_temp_update(const int32 *samples);

void wt_forecast_temp(int32 *forecast, int32 forecastLength);

void wt_forecast_type(const char *rawSamples, const int32 *tempSamples, int32 forecastLength, char *forecast);

uint64 wt_sign(const char *data, int32 length);