package cartographer.providers

import java.time.ZoneOffset
import java.time.ZonedDateTime

class DateTimeProviderUtc : DateTimeProvider {
    override fun get(): ZonedDateTime = ZonedDateTime.now(ZoneOffset.UTC)
}