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
        private val logger = LogManager.getFormatterLogger()!!

        private val defaultFilePath = "config/cartographer.yaml"
        private val filePathPropertyName = "yaml.settings.container.file.path"
    }

    private lateinit var container: Map<String, Any>
    private var initialized: Boolean = false

    override fun getSettingValue(key: String): String? {
        if (!initialized) {
            init();
        }

        return container[key]?.toString()
    }

    private fun init() {
        val filePath = System.getProperty(filePathPropertyName, defaultFilePath)

        try {
            val objectMapper = ObjectMapper(YAMLFactory())
            val file = File(filePath)
            val serialized = file.readText()

            container = objectMapper.readValue(serialized, HashMap<String, Any>().javaClass)
        } catch (t: Throwable) {
            logger.warn("Failed to initialize settings from file '$filePath' due to $t")
            container = emptyMap()
        }

        initialized = true
    }
}