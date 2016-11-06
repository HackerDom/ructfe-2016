package cartographer.configs

import cartographer.settings.SettingsContainer
import cartographer.settings.StringSetting
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
open class CryptographyConfig {
    companion object {
        private val cipherSpecSetting = StringSetting("cryptography.cipher_spec", "")
        private val keySpecSetting = StringSetting("cryptography.key_spec", "AES (128)")

        lateinit var cipherSpec: String
        lateinit var keySpec:String
    }

    @Bean
    fun init(settingsContainer: SettingsContainer) {
        cipherSpec = cipherSpecSetting.getValue(settingsContainer)
        keySpec = keySpecSetting.getValue(settingsContainer)
    }
}