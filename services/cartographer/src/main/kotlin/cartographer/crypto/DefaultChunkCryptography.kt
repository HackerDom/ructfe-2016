package cartographer.crypto

import cartographer.data.ChunkMetadata
import cartographer.helpers.bytesToInt
import cartographer.helpers.intToBytes
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.stereotype.Component
import java.security.InvalidKeyException
import java.security.Key

@Component
class DefaultChunkCryptography(val cryptography: Cryptography,
                               val keyDeserializer: KeyDeserializer,
                               val objectMapper: ObjectMapper) : ChunkCryptography {

    override fun encrypt(sessionKey: Key, masterKey: Key, plaintext: ByteArray): ByteArray {
        val metadata = ChunkMetadata(sessionKey.encoded)
        val metadataSerialized = objectMapper.writeValueAsBytes(metadata)
        val metadataEncrypted = cryptography.encrypt(masterKey, metadataSerialized)
        val metadataEncryptedLength = intToBytes(metadataEncrypted.size)

        val ciphertext = cryptography.encrypt(sessionKey, plaintext)

        return byteArrayOf(*metadataEncryptedLength, *metadataEncrypted, *ciphertext)
    }

    override fun decrypt(sessionKey: Key, masterKey: Key, ciphertext: ByteArray): ByteArray {
        val metadataEncryptedLength = bytesToInt(ciphertext)
        val metadataEncrypted = ciphertext.sliceArray(4 until 4 + metadataEncryptedLength)
        val imageEncrypted = ciphertext.sliceArray(4 + metadataEncryptedLength until ciphertext.size)

        val metadataSerialized = cryptography.decrypt(masterKey, metadataEncrypted)
        val metadata = objectMapper.readValue(metadataSerialized, ChunkMetadata::class.java)

        val decryptedSessionKey = keyDeserializer.deserialize(metadata.sessionKey)
        if (decryptedSessionKey != sessionKey) {
            throw InvalidKeyException()
        }

        return cryptography.decrypt(sessionKey, imageEncrypted)
    }
}