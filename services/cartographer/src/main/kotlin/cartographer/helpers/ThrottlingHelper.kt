package cartographer.helpers

import cartographer.throttling.Throttler
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity

inline fun <TResult> throttle(throttler: Throttler, action: () -> ResponseEntity<TResult>) : ResponseEntity<TResult> {
    try {
        if (!throttler.tryAcquireResource()) {
            return ResponseEntity(HttpStatus.TOO_MANY_REQUESTS)
        }

        return action()
    } finally {
        throttler.releaseResource()
    }
}
