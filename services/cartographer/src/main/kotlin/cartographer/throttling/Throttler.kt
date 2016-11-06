package cartographer.throttling

interface Throttler {
    fun tryAcquireResource(): Boolean

    fun releaseResource()
}