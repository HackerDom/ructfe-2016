#include "matrix.h"
#include "logging.h"

#include <stdio.h>
#include <string.h>

void m_init(struct matrix *m, int32 width, int32 height, double *data)
{
	m->width = width;
	m->height = height;
	m->data = data;
}

double m_get(const struct matrix *m, int32 x, int32 y) // (col, row)
{
	if (x < 0 || x >= m->width || y < 0 || y >= m->height)
		wt_error("Failed to get matrix cell value: index is out of range");
	return m->data[x * m->height + y];
}

void m_set(struct matrix *m, int32 x, int32 y, double value)
{
	if (x < 0 || x >= m->width || y < 0 || y >= m->height)
		wt_error("Failed to set matrix cell value: index is out of range");
	m->data[x * m->height + y] = value;
}

void m_transpose(const struct matrix *src, struct matrix *dest)
{
	dest->width = src->height;
	dest->height = src->width;

	for (int32 i = 0; i < src->width; i++)
	{
		for (int32 j = 0; j < src->height; j++)
		{
			m_set(dest, j, i, m_get(src, i, j));
		}
	}
}

void m_multiply(const struct matrix *a, const struct matrix *b, struct matrix *result)
{
	result->width = b->width;
	result->height = a->height;

	for (int32 i = 0; i < a->height; i++)
	{
		for (int32 j = 0; j < b->width; j++)
		{
			double value = 0;
			for (int32 k = 0; k < b->height; k++)
				value += m_get(a, k, i) * m_get(b, j, k);

			m_set(result, j, i, value);
		}
	}
}

void m_copy(const struct matrix *src, struct matrix *dest)
{
	dest->width = src->width;
	dest->height = src->height;

	memcpy(dest->data, src->data, sizeof(double) * dest->width * dest->height);
}

void m_identity(struct matrix *m)
{
	memset(m->data, 0, sizeof(double) * m->width * m->height);

	for (int32 i = 0; i < min(m->width, m->height); i++)
		m_set(m, i, i, 1);
}

void swap_rows(struct matrix *m, int32 row1, int32 row2)
{
	for (int32 i = 0; i < m->width; i++)
	{
		double temp = m_get(m, i, row1);
		m_set(m, i, row1, m_get(m, i, row2));
		m_set(m, i, row2, temp);
	}
}

void find_nonzeros_below(const struct matrix *m, int32 row, int32 col, int32 *nonzeroCount, int32 *firstNonzero)
{
	*nonzeroCount = 0;
	*firstNonzero = -1;

	for (int32 i = row; i < m->height; i++)
	{
		if (abs(m_get(m, col, row)) < M_EPS)
			continue;

		if (*firstNonzero < 0)
			*firstNonzero = i;

		(*nonzeroCount)++;
	}
}

void m_display_matrix(const struct matrix *m)
{
	char buffer[256];
	char temp[256];
	for (int32 i = 0; i < m->height; i++)
	{
		memset(buffer, 0, sizeof(buffer));

		for (int32 j = 0; j < m->width; j++)
		{
			memset(temp, 0, sizeof(temp));

			sprintf(temp, "%lf ", m_get(m, j, i));

			strcat(buffer, temp);
		}

		wt_log_info("%s", buffer);
	}
}

void m_invert(const struct matrix *src, struct matrix *dest, struct matrix *temp)
{
	dest->width = src->width;
	dest->height = src->height;

	m_identity(dest);

	temp->width = src->width * 2;
	temp->height = src->height;

	for (int32 i = 0; i < temp->width; i++)
	{
		for (int32 j = 0; j < temp->height; j++)
		{
			if (i < src->width)
				m_set(temp, i, j, m_get(src, i, j));
			else
				m_set(temp, i, j, m_get(dest, i - src->width, j));
		}
	}

	int32 row = 0;
	for (int32 col = 0; col < temp->width; col++)
	{
		int32 firstNonzero;
		int32 nonzeroCount;

		find_nonzeros_below(temp, row, col, &nonzeroCount, &firstNonzero);

		if (nonzeroCount == 0)
		{
			if (col == temp->width - 1)
				break;

			wt_log_error("Failed to invert matrix: matrix is singular");
			return;
		}

		if (firstNonzero != row)
			swap_rows(temp, row, firstNonzero);

		double savedValue = m_get(temp, col, row);
		for (int32 j = 0; j < temp->width; j++)
			m_set(temp, j, row, m_get(temp, j, row) / savedValue);

		for (int32 j = 0; j < temp->height; j++)
		{
			if (j == row)
				continue;

			double savedValue = m_get(temp, col, j);
			for (int32 k = 0; k < temp->width; k++)
			{
				double scaled_value = savedValue * m_get(temp, k, row);
				m_set(temp, k, j, m_get(temp, k, j) - scaled_value);
			}
		}

		row++;

		if (row >= temp->height)
			break;
	}

	for (int32 i = 0; i < dest->width; i++)
	{
		for (int32 j = 0; j < dest->height; j++)
		{
			m_set(dest, i, j, m_get(temp, i + src->width, j));
		}
	}
}