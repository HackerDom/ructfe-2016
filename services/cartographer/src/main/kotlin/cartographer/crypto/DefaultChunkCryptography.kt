package cartographer.crypto

import java.security.Key

class DefaultChunkCryptography : ChunkCryptography {
    override fun decrypt(sessionKey: Key, masterKey: Key, ciphertext: ByteArray): ByteArray {
        // TODO Implement
        throw UnsupportedOperationException("not implemented") //To change body of created functions use File | Settings | File Templates.
    }

    override fun encrypt(sessionKey: Key, masterKey: Key, plaintext: ByteArray): ByteArray {
        // TODO Implement
        throw UnsupportedOperationException("not implemented") //To change body of created functions use File | Settings | File Templates.
    }
}