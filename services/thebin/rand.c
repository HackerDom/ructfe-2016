#include <stdio.h>

typedef struct {
	unsigned long long state;
	unsigned value;
} result_t;

inline unsigned rol(const unsigned value, short n) {
	return (value << n) | (value >> (8 * sizeof(unsigned) - n));
}

inline unsigned ror(const unsigned value, short n) {
	return (value >> n) | (value << (8 * sizeof(unsigned) - n));
}

extern result_t next(unsigned long long state) {
//	unsigned s = state;
//	s += 0x51ae4f20u;
//	s = rol(s, 7);
//	s ^= 0xf2f4ea15u;
//	s -= 0x15eaf402u;
//	s = rol(s, 15);
//	result_t result;
//	result.state = s + 3184007659u;
//	result.value = rol(s, 5);
//	unsigned s = state;
//	s += 0x51ae4f20u;
//	s = rol(s, 7);
//	s ^= 0xf2f4ea15u;
//	s -= 0x15eaf402u;
//	s = rol(s, 16);
//	result_t result;
//	result.state = s + 3184007659u;
//	result.value = rol(s, 5);
//	return result;

	unsigned s = state;

	s += 0x9c039f7fu;
	s ^= 0x740ca70cu;
	s = rol(s, 15);

	if (s) {
		unsigned long long n = s;
		unsigned long long b = n & (~n >> 1);
		unsigned long long l = b ^ (b & (b - 1));

		n ^= l;
		n ^= l << 1;

		unsigned long long t = n & (l - 1);
		n &= ~(l - 1);

		while (t && !(t & 1))
			t >>= 1;

		n |= t;
		s = n;
	}
	else {
		s = ~0u;
	}

	s = ror(s, 15);
	s ^= 0x740ca70cu;
	s -= 0x9c039f7fu;

	result_t result;
	result.state = s;
	result.value = (unsigned)s ^ 0xdd742523;

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
