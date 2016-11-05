#include "rand.c"
#include <cstdio>
#include <vector>

int main() {
	std::vector<bool> used(1ull << 32);

	unsigned start = 0;
	unsigned long long result = 1ull << 32;
	do {
		unsigned long long pos = start;
		if (used[pos])
			continue;
		printf("start from %llu\n", pos);
		fflush(stdout);
		unsigned long long length = 0;
		while (!used[pos]) {
			used[pos] = 1;
			++length;
			pos = next(pos).state;
			if (length % 10000000)
				continue;
			printf("length %010llu, pos %llu\n", length, pos);
			fflush(stdout);
		}

		if (pos != start) {
			printf("Error: not a circle!!!\n");
			return 0;
		}

		if (length < result)
			result = length;
		printf("%u %llu\n", start, length);
		fflush(stdout);
	}
	while (++start);
	printf("%llu\n", result);

	return 0;
}
