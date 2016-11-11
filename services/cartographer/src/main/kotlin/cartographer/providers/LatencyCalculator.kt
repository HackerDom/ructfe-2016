package cartographer.providers

import java.net.InetSocketAddress
import java.time.Duration

interface LatencyCalculator {
    fun CalcLatency(addr: InetSocketAddress, maxAllowedDuration: Duration): Long?
}