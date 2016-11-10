package cartographer.throttling

import cartographer.settings.DurationSetting
import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import org.springframework.stereotype.Component
import java.time.Duration
import java.util.concurrent.Semaphore
import java.util.concurrent.TimeUnit

@Component
class StaticThrottler : Throttler {
    companion object {
        val maxConcurrentRequestsSetting = IntSetting("throttler.max_concurrent_requests", 100)
        val timeoutSetting = DurationSetting("throttler.timeout", Duration.ofSeconds(30))
    }

    val semaphore: Semaphore
    val timeout: Duration

    constructor(settingsContainer: SettingsContainer) {
        val maxConcurrentRequests = maxConcurrentRequestsSetting.getValue(settingsContainer)
        semaphore = Semaphore(maxConcurrentRequests)
        timeout = timeoutSetting.getValue(settingsContainer)
    }

    override fun tryAcquireResource(): Boolean {
        return semaphore.tryAcquire(timeout.toMillis(), TimeUnit.MILLISECONDS)
    }

    override fun releaseResource() {
        semaphore.release()
    }
}