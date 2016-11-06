package cartographer.settings

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import org.apache.logging.log4j.LogManager
import org.springframework.stereotype.Component
import java.io.File
import java.util.HashMap

@Component
class YamlSettingsContainer : SettingsContainer {
    companion object {
        val logger = LogManager.getFormatterLogger()!!

        val defaultFilePath = "config.yaml"
        val filePathPropertyName = "yaml.settings.container.file.path"
    }

    lateinit var container: Map<String, String>
    var initialized: Boolean = false

    override fun getSettingValue(key: String): String? {
        if (!initialized) {
            init();
        }

        return container.get(key)
    }

    private fun init() {
        val filePath = System.getProperty(filePathPropertyName, defaultFilePath)

        try {
            val objectMapper = ObjectMapper(YAMLFactory())
            val file = File(filePath)
            val serialized = file.readText()

            container = objectMapper.readValue(serialized, HashMap<String, String>().javaClass)
        } catch (t: Throwable) {
            logger.warn("Failed to initialize settings from file '$filePath' due to $t")
            container = emptyMap()
        }

        initialized = true
    }
}