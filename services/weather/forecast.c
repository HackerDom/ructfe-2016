#include "forecast.h"
#include "logging.h"
#include "matrix.h"

#include <string.h>

#define SMA_PERIOD 4

double forecastPoly[WT_POLY_POWER + 1];

int32 normalize_sample(char sample)
{
	// range: -5 ~ +25

	return (int32)sample * 30 / 255 - 5;
}

void wt_forecast_temp_prepare(const char *rawSamples, int32 *samples)
{
	double acc = 0;
	int32 count = 0;
	for (int32 i = 0; i < WT_SAMPLES; i++)
	{
		acc += normalize_sample(rawSamples[i]);

		if (count < SMA_PERIOD)
			count++;
		else
			acc -= normalize_sample(rawSamples[i - SMA_PERIOD]);

		samples[i] = (int32)(acc / count);
	}
}

void poly_fit(const int32 *samples, double *polyData)
{
	struct matrix y, X, a, Xt, X2, X2inv, X2temp;

	double datay[WT_SAMPLES];
	double dataX[WT_SAMPLES * (WT_POLY_POWER + 1)];
	double dataXt[WT_SAMPLES * (WT_POLY_POWER + 1)];
	double dataX2[WT_SAMPLES * WT_SAMPLES];
	double dataX2inv[WT_SAMPLES * WT_SAMPLES];
	double dataX2temp[WT_SAMPLES * WT_SAMPLES * 2];

	m_init(&y, 1, WT_SAMPLES, datay);
	m_init(&X, WT_POLY_POWER + 1, WT_SAMPLES, dataX);
	m_init(&a, 1, WT_POLY_POWER + 1, polyData);
	m_init(&Xt, WT_SAMPLES, WT_POLY_POWER + 1, dataXt);
	m_init(&X2, WT_SAMPLES, WT_SAMPLES, dataX2);
	m_init(&X2inv, WT_SAMPLES, WT_SAMPLES, dataX2inv);
	m_init(&X2temp, WT_SAMPLES * 2, WT_SAMPLES, dataX2temp);

	for (int32 i = 0; i < WT_SAMPLES; i++)
		m_set(&y, 0, i, samples[i]);

	for (int32 i = 0; i < WT_SAMPLES; i++)
	{
		double value = 1;
		for (int32 j = 0; j < WT_POLY_POWER + 1; j++)
		{
			m_set(&X, j, i, value);

			value *= i;
		}
	}

	m_transpose(&X, &Xt);
	m_multiply(&Xt, &X, &X2);
	m_invert(&X2, &X2inv, &X2temp);
	m_multiply(&X2inv, &Xt, &X2temp);
	m_multiply(&X2temp, &y, &a);

	m_display_matrix(&a);
}

void wt_forecast_temp_update(const int32 *samples)
{
	poly_fit(samples, forecastPoly);
}

double eval_poly(double x)
{
	double result = forecastPoly[WT_POLY_POWER];

	for (int32 i = WT_POLY_POWER - 1; i >= 0; i--)
		result = x * result + forecastPoly[i];

	return result;
}

void wt_forecast_temp(int32 *forecast, int32 forecastLength)
{
	for (int32 i = 0; i < forecastLength; i++)
		forecast[i] = (int32)eval_poly(i + WT_SAMPLES);
}

void wt_forecast_type(const char *rawSamples, const int32 *tempSamples, int32 forecastLength, char *forecast)
{
	for (int32 i = 0; i < forecastLength; i++)
	{
		char type = rawSamples[i] % 6;

		if (type > WT_CLOUDY)
		{
			if (tempSamples[i] < 0)
				type = WT_SNOW;
			else if (tempSamples[i] < 15)
				type = WT_RAIN;
		}

		forecast[i] = type;
	}
}

uint64 wt_sign(const char *data, int32 length)
{
	int32 samples[WT_SAMPLES];

	memset(samples, 0, sizeof(samples));

	for (int32 i = 0; i < length; i++)
		samples[i % WT_SAMPLES] = data[i];

	double poly[WT_POLY_POWER + 1];

	poly_fit(samples, poly);

	return *(uint64 *)&poly;
}