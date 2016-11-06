package cartographer.helpers

import cartographer.providers.DateTimeProvider
import cartographer.providers.DateTimeProviderUtc
import cartographer.testhelpers.waitUntil
import org.hamcrest.Matchers
import org.junit.Assert
import org.junit.Test
import java.time.Duration
import java.time.ZonedDateTime
import java.util.concurrent.atomic.AtomicInteger

class PeriodicalActionTest {
    companion object {
        val dateTimeProvider: DateTimeProvider = DateTimeProviderUtc()
    }

    @Test
    fun PeriodicalAction_should_be_invoked_action_right_after_start() {
        val int = AtomicInteger()
        PeriodicalAction(Duration.ofDays(1), dateTimeProvider, { int.incrementAndGet() }).use {
            waitUntil(Duration.ofSeconds(1)) {
                int.get() == 1
            }
        }
    }

    @Test
    fun PeriodicalAction_should_wait_only_the_rest_of_period() {
        var firstTime : ZonedDateTime? = null
        var secondTime : ZonedDateTime? = null
        val action = {
            if (firstTime == null) {
                firstTime = dateTimeProvider.get()
            } else if (secondTime == null) {
                secondTime = dateTimeProvider.get()
            }

            Thread.sleep(50)
        }

        PeriodicalAction(Duration.ofMillis(100), dateTimeProvider, action).use {
            waitUntil(Duration.ofSeconds(1)) {
                secondTime != null
            }

            Assert.assertThat(durationBetween(firstTime!!, secondTime!!).toMillis(), Matchers.lessThan(110L))
        }
    }

    @Test
    fun PeriodicalAction_should_not_stop_if_exception_occurred_in_action() {
        val int = AtomicInteger()
        PeriodicalAction(Duration.ofMillis(100), dateTimeProvider, { int.incrementAndGet(); throw Exception() }).use {
            waitUntil(Duration.ofSeconds(1)) {
                int.get() == 2
            }
        }
    }
}