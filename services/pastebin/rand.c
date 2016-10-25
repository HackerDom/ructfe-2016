#include <stdio.h>

typedef struct {
	unsigned long long state;
	unsigned value;
} result_t;

unsigned rol(const unsigned value, short n) {
	n &= 31;
	return (value << n) | (value >> (32 - n));
}

extern result_t next(unsigned long long state) {
	unsigned s = state;
	s += 0x51ae4f20u;
	s = rol(s, 7);
	s ^= 0xf2f4ea15u;
	s -= 0x15eaf402u;
	s = rol(s, 15);
	result_t result;
	result.state = s + 1;
	result.value = rol(s, 5);
	return result;
}

extern unsigned long long init() {
	unsigned long long res = 0;
	FILE* in = fopen("/dev/urandom", "r");
	if (fread(&res, sizeof(res), 1, in) <= 0)
		res = 0x12ab67f0u;
	fclose(in);

	return res;
}
