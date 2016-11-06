package cartographer.crypto

import org.springframework.stereotype.Component
import java.security.Key
import java.security.SecureRandom
import javax.crypto.KeyGenerator

@Component
class DefaultKeyGenerator(val cryptographySettings: CryptographySettings) : cartographer.crypto.KeyGenerator {
    private val secureRandom = SecureRandom()

    override fun generate(): Key {
        val keyGenerator = KeyGenerator.getInstance(cryptographySettings.keySpec)
        keyGenerator.init(128, secureRandom)
        return keyGenerator.generateKey()
    }
}