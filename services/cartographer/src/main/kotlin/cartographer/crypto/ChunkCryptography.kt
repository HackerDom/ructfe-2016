package cartographer.crypto

import java.security.Key

interface ChunkCryptography {
    fun encrypt(sessionKey: Key, masterKey: Key, plaintext: ByteArray): ByteArray

    fun decrypt(sessionKey: Key, masterKey: Key, ciphertext: ByteArray): ByteArray
}