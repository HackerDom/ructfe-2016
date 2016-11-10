package cartographer.providers

import java.net.InetSocketAddress

interface LatencyCalculator {
    fun CalcLatency(addr: InetSocketAddress): Long?
}