package cartographer.helpers

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

    constructor(period: Duration, action: () -> Unit) {
        workingThread = thread {
            try {
                while (true) {
                    val startTime = ZonedDateTime.now(ZoneOffset.UTC)

                    try {
                        action()
                    } catch (t: InterruptedException) {
                        break;
                    } catch (t: Throwable) {
                        logger.error("Failed to execute action $action", t)
                    }

                    val endTime = ZonedDateTime.now(ZoneOffset.UTC)
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