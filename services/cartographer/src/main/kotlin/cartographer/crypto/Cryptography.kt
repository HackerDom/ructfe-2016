package cartographer.crypto

import java.security.Key

interface Cryptography {
    fun encrypt(key: Key, plaintext: ByteArray): ByteArray

    fun decrypt(key: Key, ciphertext: ByteArray): ByteArray
}