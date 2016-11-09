#include <stdio.h>
#include <stdlib.h>

typedef unsigned long long ull;

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

unsigned pre(unsigned value) {
	unsigned s = value ^ 0xdd742523;

	s += 0x9c039f7fu;
	s ^= 0x740ca70cu;
	s = rol(s, 15);

	return s;
}

unsigned post(unsigned s) {
	s = ror(s, 15);
	s ^= 0x740ca70cu;
	s -= 0x9c039f7fu;
	return s ^ 0xdd742523;
}

unsigned next(unsigned value) {
	unsigned s = pre(value);

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

	return post(s);
}

unsigned prev(unsigned value) {
	unsigned s = pre(value);

	if (~s) {
		ull n = s | (1ull << 32);
		ull b = n & (~n << 1);
		ull l = b ^ (b & (b - 1));

		n ^= l;
		l >>= 1;
		n ^= l;
  	if (l > 1) {
			ull t = n & (l - 1);
			n &= ~(l - 1);
			l >>= 1;
			while (t && !(t & l))
				t <<= 1;
			n |= t;
		}
		s = n;
	}
	else {
		s = 0;
	}

	return post(s);
}

extern unsigned long long init() {
	unsigned long long res = 0;
	FILE* in = fopen("/dev/urandom", "r");
	if (fread(&res, sizeof(res), 1, in) <= 0)
		res = 0x12ab67f0u;
	fclose(in);

	return res;
}


int main(int argc, char **argv) {
	unsigned x = atoi(argv[1]);
	printf("%u\n", next(x));
	printf("%u\n", prev(x));
	return 0;
}