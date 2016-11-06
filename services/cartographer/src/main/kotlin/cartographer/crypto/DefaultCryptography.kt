package cartographer.crypto

import org.springframework.stereotype.Component
import java.security.Key
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec

@Component
class DefaultCryptography(val cryptographySettings: CryptographySettings) : Cryptography {
    override fun encrypt(key: Key, plaintext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(cryptographySettings.cipherSpec)
        cipher.init(Cipher.ENCRYPT_MODE, key, IvParameterSpec(key.encoded))
        return cipher.doFinal(plaintext)
    }

    override fun decrypt(key: Key, ciphertext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(cryptographySettings.cipherSpec)
        cipher.init(Cipher.DECRYPT_MODE, key, IvParameterSpec(key.encoded))
        return cipher.doFinal(ciphertext)
    }
}