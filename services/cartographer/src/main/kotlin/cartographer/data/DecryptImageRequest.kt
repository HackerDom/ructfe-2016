package cartographer.data

import com.fasterxml.jackson.annotation.JsonProperty

data class DecryptImageRequest(@JsonProperty("key") val key: ByteArray,
                               @JsonProperty("id") val id: String?,
                               @JsonProperty("chunk") val chunk: ByteArray?)