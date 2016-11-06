package cartographer.crypto

import org.springframework.stereotype.Component
import java.security.Key
import javax.crypto.spec.SecretKeySpec

@Component
class DefaultKeyDeserializer(val cryptographySettings: CryptographySettings) : KeyDeserializer {
    override fun deserialize(serialized: ByteArray): Key {
        return SecretKeySpec(serialized, cryptographySettings.keySpec)
    }
}