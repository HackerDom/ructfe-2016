package cartographer.providers

import java.net.InetAddress

interface LatencyCalculator {
    fun CalcLatency(addr: InetAddress): Long?
}