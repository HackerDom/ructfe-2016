package cartographer.providers

import org.springframework.stereotype.Component
import java.time.ZoneOffset
import java.time.ZonedDateTime

@Component
class DateTimeProviderUtc : DateTimeProvider {
    override fun get(): ZonedDateTime = ZonedDateTime.now(ZoneOffset.UTC)
}