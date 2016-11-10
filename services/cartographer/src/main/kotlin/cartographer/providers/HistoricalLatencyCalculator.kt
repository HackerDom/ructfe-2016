package cartographer.providers

import cartographer.data.AddressLatencyHistory
import cartographer.data.SynchronizeTimeRequest
import cartographer.data.SynchronizeTimeResponse
import cartographer.helpers.durationBetween
import cartographer.settings.DoubleSetting
import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import cartographer.settings.StringSetting
import com.fasterxml.jackson.databind.ObjectMapper
import org.apache.logging.log4j.LogManager
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.stereotype.Component
import org.springframework.web.client.RestTemplate
import java.net.InetSocketAddress
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

@Component
class HistoricalLatencyCalculator : LatencyCalculator {
    companion object {
        private val movingAverageExponentSetting = DoubleSetting("latency_calculator.ema_exponent", 0.2)
        private val endpointSetting = StringSetting("latency_calculator.endpoint", "timesync")
    }

    private val history: ConcurrentMap<InetSocketAddress, AddressLatencyHistory> =
            ConcurrentHashMap<InetSocketAddress, AddressLatencyHistory>()

    private val movingAverageExponent: Double
    private val endpoint: String

    private val objectMapper: ObjectMapper
    private val dateTimeProvider: DateTimeProvider

    constructor(dateTimeProvider: DateTimeProvider, objectMapper: ObjectMapper, settingsContainer: SettingsContainer) {
        movingAverageExponent = movingAverageExponentSetting.getValue(settingsContainer)
        endpoint = endpointSetting.getValue(settingsContainer)

        this.objectMapper = objectMapper
        this.dateTimeProvider = dateTimeProvider
    }

    override fun CalcLatency(addr: InetSocketAddress): Long? {
        val addressHistory = history.getOrPut(addr, { AddressLatencyHistory(null) })
        val newAddressHistory = calcNewHistory(addr, addressHistory)
        history.put(addr, newAddressHistory)
        return newAddressHistory.averageLatency
    }

    private fun calcNewHistory(addr: InetSocketAddress,
                               addressHistory: AddressLatencyHistory): AddressLatencyHistory {
        val latency = tryCalcLatency(addr)

        if (latency != null) {
            if (addressHistory.averageLatency == null) {
                return AddressLatencyHistory(latency)
            }

            val newLatencyValue = latency * movingAverageExponent +
                    addressHistory.averageLatency * (1 - movingAverageExponent)
            return AddressLatencyHistory(newLatencyValue.toLong())
        }

        return AddressLatencyHistory(null)
    }

    private fun tryCalcLatency(addr: InetSocketAddress): Long? {
        try {
            val request = SynchronizeTimeRequest(dateTimeProvider.get())
            val requestSerialized = objectMapper.writeValueAsString(request)
            val responseSerialized = sendRequest(addr, requestSerialized)

            val response = objectMapper.readValue(responseSerialized, SynchronizeTimeResponse::class.java)

            return if (response != null) calcLatencyFromResponse(response) else null
        } catch (t: Throwable) {
            return null
        }
    }

    private fun sendRequest(addr: InetSocketAddress, requestSerialized: String): String? {
        val uri = "http://${addr.hostName}:${addr.port}/$endpoint"

        val headers = HttpHeaders()
        headers.add("Content-Type", "application/json")
        headers.add("Accept", "*/*")

        val rest = RestTemplate()
        val requestEntity = HttpEntity<String>(requestSerialized, headers)

        val responseEntity = rest.exchange(uri, HttpMethod.POST, requestEntity, String::class.java)

        if (!responseEntity.statusCode.is2xxSuccessful) {
            return null
        }

        return responseEntity.body
    }

    private fun calcLatencyFromResponse(response: SynchronizeTimeResponse): Long {
        val localDelta = durationBetween(response.sendRequestTime, dateTimeProvider.get())
        val remoteDelta = durationBetween(response.receiveRequestTime, response.sendResponseTime)

        return localDelta.minus(remoteDelta).dividedBy(2).toMillis()
    }
}

