package cartographer.settings

class IntSetting : Setting<Int> {
    constructor(key: String) : super(key, { str -> Integer.parseInt(str) })

    constructor(key: String, defaultValue: Int) : super(key, { str -> Integer.parseInt(str) }, defaultValue)
}