package cartographer.testhelpers

import java.time.Duration
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.concurrent.TimeoutException

fun waitUntil(duration: Duration, action: () -> Boolean) {
    val testEnd = ZonedDateTime.now(ZoneOffset.UTC).plus(duration)
    while (ZonedDateTime.now(ZoneOffset.UTC).isBefore(testEnd)) {
        if (action()) {
            return
        }
    }

    throw TimeoutException()
}