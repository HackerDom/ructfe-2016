package cartographer.settings

class SettingsParseException(key: String, valueString: String, ex: Throwable)
: Exception("Could not parse setting '$key' with value $valueString", ex)