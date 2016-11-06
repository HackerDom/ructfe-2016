package cartographer.helpers

import cartographer.providers.DateTimeProvider
import org.apache.logging.log4j.LogManager
import java.io.Closeable
import java.time.*
import kotlin.concurrent.thread

class PeriodicalAction : Closeable {
    companion object {
        val logger = LogManager.getFormatterLogger()!!
    }

    val workingThread: Thread

    override fun close() {
        workingThread.interrupt()
    }

    constructor(period: Duration, dateTimeProvider: DateTimeProvider, action: () -> Unit) {
        workingThread = thread {
            try {
                while (true) {
                    val startTime = dateTimeProvider.get()

                    try {
                        action()
                    } catch (t: InterruptedException) {
                        break
                    } catch (t: Throwable) {
                        logger.error("Failed to execute action $action", t)
                    }

                    val endTime = dateTimeProvider.get()
                    val runDuration = durationBetween(startTime, endTime)
                    val toWait = period.minus(runDuration)

                    if (!toWait.isNegative) {
                        Thread.sleep(toWait.toMillis())
                    }
                }
            } catch (t: InterruptedException) {
                // Everything is fine
            }
        }
    }
}