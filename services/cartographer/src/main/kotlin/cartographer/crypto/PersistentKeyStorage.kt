package cartographer.crypto

import cartographer.settings.SettingsContainer
import cartographer.settings.StringSetting
import org.apache.logging.log4j.LogManager
import org.springframework.stereotype.Component
import java.io.File
import java.security.Key
import javax.crypto.spec.SecretKeySpec

@Component
class PersistentKeyStorage : KeyStorage {
    companion object {
        val keyFileNameSetting = StringSetting("key_storage.key_file_name", "master.key")

        val logger = LogManager.getFormatterLogger()!!
    }

    val keyFileName: String
    val keyGenerator: KeyGenerator

    val locker: Any = Any()

    @Volatile
    lateinit var key: Key
    @Volatile
    var initialized: Boolean = false

    constructor(settingsContainer: SettingsContainer, keyGenerator: KeyGenerator) {
        keyFileName = keyFileNameSetting.getValue(settingsContainer)
        this.keyGenerator = keyGenerator
    }

    override fun get(): Key {
        if (initialized) {
            return key
        }

        synchronized(locker) {
            if (initialized) {
                return key
            }

            try {
                key = tryReadFromFile(keyFileName)
            } catch (t: Throwable) {
                logger.warn("Failed to read key from '$keyFileName', generating new")

                key = keyGenerator.generate()
                saveToFile(key, keyFileName)
            }

            return key
        }
    }

    private fun saveToFile(key: Key, keyFileName: String) {
        val file = File(keyFileName)
        file.writeBytes(key.encoded)
    }

    private fun tryReadFromFile(keyFileName: String): Key {
        val file = File(keyFileName)
        val bytes = file.readBytes()
        return SecretKeySpec(bytes, DefaultKeyGenerator.keyGeneratorSpec)
    }
}