#pragma once

#include "types.h"

#define M_EPS 1e-9

struct matrix
{
	int32 width;
	int32 height;
	double *data;
};

void m_init(struct matrix *m, int32 width, int32 height, double *data);

double m_get(const struct matrix *m, int32 x, int32 y);

void m_set(struct matrix *m, int32 x, int32 y, double value);

void m_transpose(const struct matrix *src, struct matrix *dest);

void m_multiply(const struct matrix *a, const struct matrix *b, struct matrix *result);

void m_copy(const struct matrix *src, struct matrix *dest);

void m_identity(struct matrix *m);

void m_display_matrix(const struct matrix *m);

void m_invert(const struct matrix *src, struct matrix *dest, struct matrix *temp);