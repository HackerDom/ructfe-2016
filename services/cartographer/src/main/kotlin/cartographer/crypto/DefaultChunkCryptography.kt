package cartographer.crypto

import cartographer.configs.CryptographyConfig
import cartographer.data.ChunkMetadata
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.stereotype.Component
import java.nio.ByteBuffer
import java.security.InvalidKeyException
import java.security.Key
import javax.crypto.spec.SecretKeySpec

@Component
class DefaultChunkCryptography(val cryptography: Cryptography, val objectMapper: ObjectMapper) : ChunkCryptography {
    override fun encrypt(sessionKey: Key, masterKey: Key, plaintext: ByteArray): ByteArray {
        val metadata = ChunkMetadata(sessionKey.encoded)
        val metadataSerialized = objectMapper.writeValueAsBytes(metadata)
        val metadataEncrypted = cryptography.encrypt(masterKey, metadataSerialized)
        val metadataEncryptedLength = intToBytes(metadataEncrypted.size)

        val ciphertext = cryptography.encrypt(sessionKey, plaintext)

        return byteArrayOf(*metadataEncryptedLength, *metadataEncrypted, *ciphertext)
    }

    override fun decrypt(sessionKey: Key, masterKey: Key, ciphertext: ByteArray): ByteArray {
        val metadataEncryptedLength = bytesToInt(ciphertext.slice(0..3).toByteArray())
        val metadataEncrypted = ciphertext.slice(4..(4 + metadataEncryptedLength - 1)).toByteArray()
        val imageEncrypted = ciphertext.slice((4 + metadataEncryptedLength)..(ciphertext.size - 1)).toByteArray()

        val metadataSerialized = cryptography.decrypt(masterKey, metadataEncrypted)
        val metadata = objectMapper.readValue(metadataSerialized, ChunkMetadata::class.java)

        val decryptedSessionKey = SecretKeySpec(metadata.sessionKey, CryptographyConfig.keySpec)
        if (decryptedSessionKey != sessionKey) {
            throw InvalidKeyException()
        }

        return cryptography.decrypt(sessionKey, imageEncrypted)
    }

    private fun  bytesToInt(bytes: ByteArray): Int {
        return ByteBuffer.wrap(bytes).int
    }

    private fun intToBytes(size: Int): ByteArray {
        return ByteBuffer.allocate(4).putInt(size).array()
    }
}