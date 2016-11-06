package cartographer.helpers

import java.time.Duration
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit

fun durationBetween(lhs: ZonedDateTime, rhs: ZonedDateTime) : Duration {
    return Duration.ofNanos(ChronoUnit.NANOS.between(lhs, rhs))
}