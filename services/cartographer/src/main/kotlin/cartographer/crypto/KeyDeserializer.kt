package cartographer.crypto

import java.security.Key

interface KeyDeserializer {
    fun deserialize(serialized: ByteArray): Key
}