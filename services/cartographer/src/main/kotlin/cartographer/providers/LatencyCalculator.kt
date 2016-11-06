package cartographer.providers

import java.net.InetAddress
import java.time.Duration

interface LatencyCalculator {
    fun CalcLatency(addr: InetAddress, maxAllowedLatency: Duration): Long?
}