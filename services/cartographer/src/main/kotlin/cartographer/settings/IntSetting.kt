package cartographer.settings

class IntSetting : Setting<Int> {
    constructor(key: String) : super(key, String::toInt)

    constructor(key: String, defaultValue: Int) : super(key, String::toInt, defaultValue)
}

