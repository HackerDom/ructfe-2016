package cartographer.settings

class DoubleSetting : Setting<Double> {
    constructor(key: String) : super(key, String::toDouble)

    constructor(key: String, defaultValue: Double) : super(key, String::toDouble, defaultValue)
}