package cartographer.testhelpers

import java.time.Duration
import java.time.Instant
import java.util.concurrent.TimeoutException

fun waitUntil(duration: Duration, action: () -> Boolean) {
    val testEnd = Instant.now().plus(duration)
    while (Instant.now().isBefore(testEnd)) {
        if (action()) {
            return
        }
    }

    throw TimeoutException()
}