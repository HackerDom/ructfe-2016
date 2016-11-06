package cartographer.settings

interface SettingsContainer {
    fun getSettingValue(key: String) : String?
}