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
        private val keyFileNameSetting = StringSetting("key_storage.key_file_name", "master.key")

        private val logger = LogManager.getFormatterLogger()!!
    }

    private val keyFileName: String
    private val keyGenerator: KeyGenerator

    private val locker: Any = Any()

    @Volatile
    private lateinit var key: Key
    @Volatile
    private var initialized: Boolean = false

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

            initialized = true

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