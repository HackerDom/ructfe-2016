package cartographer.data

import com.fasterxml.jackson.annotation.JsonProperty

data class EncryptImageResponse(@JsonProperty("id") val id: String,
                                @JsonProperty("key") val key: ByteArray,
                                @JsonProperty("replicas") val replicas: List<Replica>)