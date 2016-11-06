package cartographer.settings

open class Setting<TValue> {
    private val key: String
    private val required: Boolean
    private val parse: (String) -> TValue
    private val getDefaultValue: (() -> TValue)?

    private constructor(key: String, required: Boolean, parse: (String) -> TValue, getDefaultValue: (() -> TValue)?) {
        this.key = key
        this.required = required
        this.parse = parse
        this.getDefaultValue = getDefaultValue
    }

    constructor(key: String, parse: (String) -> TValue) : this(key, true, parse, null)

    constructor(key: String, parse: (String) -> TValue, getDefaultValue: () -> TValue)
    : this(key, false, parse, getDefaultValue)

    constructor(key: String, parse: (String) -> TValue, defaultValue: TValue)
    : this(key, false, parse, { defaultValue })

    fun getValue(container: SettingsContainer): TValue {
        val valueString = container.getSettingValue(key)
        if (valueString == null) {
            if (required) {
                throw RequiredSettingMissingException(key)
            }

            return getDefaultValue!!()
        }

        try {
            return parse(valueString)
        } catch (ex: Throwable) {
            throw SettingsParseException(key, valueString, ex)
        }
    }
}

