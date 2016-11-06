package cartographer.settings

class RequiredSettingMissingException(key: String) : Throwable("Required setting '$key' is missing")