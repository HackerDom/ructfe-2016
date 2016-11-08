#pragma once

#define true 1
#define false 0

#define max(a, b) ((a) >= (b) ? (a) : (b))
#define min(a, b) ((a) <= (b) ? (a) : (b))
#define abs(n) ((n) >= 0 ? (n) : -(n))

typedef unsigned char byte;
typedef signed char sbyte;
typedef unsigned short uint16;
typedef signed short int16;
typedef unsigned int uint32;
typedef signed int int32;
typedef unsigned long long uint64;
typedef signed long long int64;
typedef int32 bool;

void wt_error(const char *message);
