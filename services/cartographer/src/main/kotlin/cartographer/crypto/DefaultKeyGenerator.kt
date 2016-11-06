package cartographer.crypto

import org.springframework.stereotype.Component
import java.security.Key
import java.security.SecureRandom
import javax.crypto.KeyGenerator

@Component
class DefaultKeyGenerator : cartographer.crypto.KeyGenerator {
    companion object {
        val keyGeneratorSpec = "AES (128)"
    }

    private val secureRandom = SecureRandom()

    override fun generate(): Key {
        val keyGenerator = KeyGenerator.getInstance(keyGeneratorSpec)
        keyGenerator.init(secureRandom)
        return keyGenerator.generateKey()
    }
}