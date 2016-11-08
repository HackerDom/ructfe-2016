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
	void *next[26];
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

bool validate_node_key(int32 nodeKey, const char *key)
{
	if (nodeKey >= 26 || nodeKey < 0)
	{
		wt_log_warn("Received a key with invalid character: %.*s", KEYSIZE, key);
		return false;
	}

	return true;
}

bool save_record(const char *key, const char *value)
{
	struct tree_node *node = &root;

	for (int32 i = 0; i < KEYSIZE - 1; i++)
	{
		int32 nodeKey = key[i] - 'a';

		if (!validate_node_key(nodeKey, key))
			return false;

		if (!node->next[nodeKey])
		{
			struct tree_node *newNode = (struct tree_node *)malloc(sizeof(struct tree_node));
			memset(newNode, 0, sizeof(struct tree_node));
			node->next[nodeKey] = newNode;
		}

		node = node->next[nodeKey];
	}

	int32 valueKey = key[KEYSIZE - 1] - 'a';

	if (!validate_node_key(valueKey, key))
		return false;

	if (node->next[valueKey])
	{
		wt_log_warn("Conflict: tried to write by already existing key: %.*s", KEYSIZE, key);
		return false;
	}

	node->next[valueKey] = malloc(VALSIZE);

	memcpy(node->next[valueKey], value, VALSIZE);

	update_last_saved((char *)node->next[valueKey]);

	return true;
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

		if (!validate_node_key(nodeKey, key))
		{
			memset(value, 0, VALSIZE);
			return;
		}

		if (!node->next[nodeKey])
		{
			memset(value, 0, VALSIZE);
			return;
		}

		node = node->next[nodeKey];
	}

	memcpy(value, node, VALSIZE);
}

void wt_storage_put(const char *key, const char *value)
{
	if (save_record(key, value))
	{
		fwrite(key, KEYSIZE, 1, storageFile);
		fwrite(value, VALSIZE, 1, storageFile);
		fflush(storageFile);
	}
}