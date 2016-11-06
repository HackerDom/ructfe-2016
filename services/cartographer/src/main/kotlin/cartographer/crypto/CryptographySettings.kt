package cartographer.crypto

import cartographer.settings.SettingsContainer
import cartographer.settings.StringSetting
import org.springframework.stereotype.Component

@Component
open class CryptographySettings {
    companion object {
        private val cipherSpecSetting = StringSetting("cryptography.cipher_spec", "AES/CBC/PKCS5Padding")
        private val keySpecSetting = StringSetting("cryptography.key_spec", "AES")
    }

    val cipherSpec: String
    val keySpec: String

    constructor(settingsContainer: SettingsContainer) {
        cipherSpec = cipherSpecSetting.getValue(settingsContainer)
        keySpec = keySpecSetting.getValue(settingsContainer)
    }
}