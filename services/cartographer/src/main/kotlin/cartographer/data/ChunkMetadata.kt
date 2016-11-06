package cartographer.data

import com.fasterxml.jackson.annotation.JsonProperty

data class ChunkMetadata(@JsonProperty("sessionKey") val sessionKey: ByteArray)