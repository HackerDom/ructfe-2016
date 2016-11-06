package cartographer.providers

import java.time.ZonedDateTime

interface DateTimeProvider {
    fun get(): ZonedDateTime
}