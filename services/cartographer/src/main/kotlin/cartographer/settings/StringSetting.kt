package cartographer.settings

class StringSetting : Setting<String> {
    constructor(key: String) : super(key, { str -> str })

    constructor(key: String, defaultValue: String) : super(key, { str -> str }, defaultValue)
}