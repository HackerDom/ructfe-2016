package cartographer.settings

import java.time.Duration

class DurationSetting : Setting<Duration> {
    constructor(key: String) : super(key, { str -> Duration.parse(str) })

    constructor(key: String, defaultValue: Duration) : super(key, { str -> Duration.parse(str) }, defaultValue)
}