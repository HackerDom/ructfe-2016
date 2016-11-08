#include "storage.h"
#include "logging.h"
#include "types.h"

#include <stdio.h>
#include <string.h>
#include <malloc.h>

#define KEYSIZE 12
#define VALSIZE 32

FILE *storageFile;

struct tree_node
{
	struct tree_node *next[26];
	char *value;
} root;

struct record
{
	char key[KEYSIZE];
	char value[VALSIZE];
};

int32 lastValuesCount;
last_values lastValues;

last_values *wt_get_last_values(int32 *available)
{
	*available = lastValuesCount;
	return &lastValues;
}

void update_last_saved(char *value)
{
	if (lastValuesCount < WT_LAST_SAVED)
	{
		lastValues[lastValuesCount] = value;
		lastValuesCount++;

		return;
	}

	for (int32 i = 1; i < WT_LAST_SAVED; i++)
		lastValues[i - 1] = lastValues[i];

	lastValues[WT_LAST_SAVED - 1] = value;
}

void save_record(const char *key, const char *value)
{
	struct tree_node *node = &root;

	for (int32 i = 0; i < KEYSIZE; i++)
	{
		int32 nodeKey = key[i] - 'a';

		if (nodeKey >= 26)
		{
			wt_log_warn("Received a key with invalid character '%c': %.*s", key[i], KEYSIZE, key);
			return;
		}

		if (!node->next[nodeKey])
		{
			struct tree_node *newNode = (struct tree_node *)malloc(sizeof(struct tree_node));
			memset(newNode, 0, sizeof(struct tree_node));
			node->next[nodeKey] = newNode;
		}

		node = node->next[nodeKey];
	}

	if (node->value)
	{
		wt_log_warn("Conflict: tried to write by already existing key: %.*s", KEYSIZE, key);
		return;
	}

	node->value = (char *)malloc(VALSIZE);

	memcpy(node->value, value, VALSIZE);

	update_last_saved(node->value);
}

void wt_init_storage(const char *filename)
{
	FILE *data = fopen(filename, "rb");

	int32 length = 0;
	if (data)
	{
		fseek(data, 0, SEEK_END);
		length = ftell(data);
		fseek(data, 0, SEEK_SET);

		length -= length % sizeof(struct record);

		struct record currentRecord;
		for (int32 i = 0; i < length; i += sizeof(currentRecord))
		{
			fread(&currentRecord, sizeof(currentRecord), 1, data);
			save_record(currentRecord.key, currentRecord.value);
		}

		fclose(data);
	}

	storageFile = fopen(filename, "r+b");

	if (!storageFile)
		storageFile = fopen(filename, "w+b");

	if (!storageFile)
		wt_error("Failed to open storage file");

	fseek(storageFile, length, SEEK_SET);
}

void wt_storage_get(const char *key, char *value)
{
	struct tree_node *node = &root;

	for (int32 i = 0; i < KEYSIZE; i++)
	{
		int32 nodeKey = key[i] - 'a';

		if (nodeKey >= 26 || nodeKey < 0)
		{
			wt_log_warn("Received a key with invalid character '%c': %.*s", key[i], KEYSIZE, key);
			return;
		}

		if (!node->next[nodeKey])
			return;

		node = node->next[nodeKey];
	}

	if (!node->value)
		return;

	memcpy(value, node->value, VALSIZE);
}

void wt_storage_put(const char *key, const char *value)
{
	fwrite(key, KEYSIZE, 1, storageFile);
	fwrite(value, VALSIZE, 1, storageFile);
	fflush(storageFile);

	save_record(key, value);
}