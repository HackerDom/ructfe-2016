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
import java.net.InetAddress
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

@Component
class HistoricalLatencyCalculator : LatencyCalculator {
    companion object {
        val movingAverageExponentSetting = DoubleSetting("latency_calculator.ema_exponent", 0.2)
        val backOffExponentSetting = IntSetting("latency_calculater.back_off_exponent", 2)
        val endpointSetting = StringSetting("latency_calculator.endpoint", "/timesync")
    }

    val history: ConcurrentMap<InetAddress, AddressLatencyHistory> =
            ConcurrentHashMap<InetAddress, AddressLatencyHistory>()
    val logger = LogManager.getFormatterLogger()!!

    val movingAverageExponent: Double
    val backOffExponent: Int
    val endpoint: String

    val objectMapper: ObjectMapper
    val dateTimeProvider: DateTimeProvider

    constructor(dateTimeProvider: DateTimeProvider, objectMapper: ObjectMapper, settingsContainer: SettingsContainer) {
        movingAverageExponent = movingAverageExponentSetting.getValue(settingsContainer)
        backOffExponent = backOffExponentSetting.getValue(settingsContainer)
        endpoint = endpointSetting.getValue(settingsContainer)

        this.objectMapper = objectMapper
        this.dateTimeProvider = dateTimeProvider
    }

    override fun CalcLatency(addr: InetAddress): Long? {
        val addressHistory = history.getOrPut(addr, { AddressLatencyHistory(null, 0, 0) })
        val newAddressHistory = calcNewHistory(addr, addressHistory)
        history.put(addr, newAddressHistory)
        return newAddressHistory.averageLatency
    }

    private fun calcNewHistory(addr: InetAddress,
                               addressHistory: AddressLatencyHistory): AddressLatencyHistory {
        if (addressHistory.backOffLeft > 0) {
            return AddressLatencyHistory(addressHistory.backOffLeft - 1, addressHistory.lastBackOff)
        }

        val latency = tryCalcLatency(addr)

        if (latency != null) {
            if (addressHistory.averageLatency == null) {
                return AddressLatencyHistory(latency)
            }

            val newLatencyValue = latency * movingAverageExponent +
                    addressHistory.averageLatency * (1 - movingAverageExponent)
            return AddressLatencyHistory(newLatencyValue.toLong())
        }

        val newBackOff = Math.max(1, addressHistory.lastBackOff * backOffExponent)
        return AddressLatencyHistory(newBackOff, newBackOff)
    }

    private fun tryCalcLatency(addr: InetAddress): Long? {
        try {
            val request = SynchronizeTimeRequest(dateTimeProvider.get())
            val requestSerialized = objectMapper.writeValueAsString(request)
            val responseSerialized = sendRequest(addr, requestSerialized)

            val response = objectMapper.readValue(responseSerialized, SynchronizeTimeResponse::class.java)

            return if (response != null) calcLatencyFromResponse(response) else null
        } catch (t: Throwable) {
            logger.warn("Failed to synchronize time with $addr due to $t")
            return null
        }
    }

    private fun sendRequest(addr: InetAddress, requestSerialized: String): String? {
        val uri = "http://${addr.hostAddress}/$endpoint"

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

