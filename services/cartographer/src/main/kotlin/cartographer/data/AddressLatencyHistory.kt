package cartographer.data

data class AddressLatencyHistory(val averageLatency: Long?,
                                 val backOffLeft: Int,
                                 val lastBackOff: Int) {
    constructor(averageLatency: Long) : this(averageLatency, 0, 0)

    constructor(backOffLeft: Int, lastBackOff: Int) : this(null, backOffLeft, lastBackOff)
}