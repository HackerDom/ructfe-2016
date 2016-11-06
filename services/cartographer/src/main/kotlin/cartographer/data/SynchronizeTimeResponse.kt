package cartographer.data

import cartographer.providers.DateTimeProvider
import com.fasterxml.jackson.annotation.JsonProperty
import java.time.ZonedDateTime

data class SynchronizeTimeResponse(@JsonProperty("sendRequestTime") val sendRequestTime: ZonedDateTime,
                                   @JsonProperty("receiveRequestTime") val receiveRequestTime: ZonedDateTime,
                                   @JsonProperty("sendResponseTime") val sendResponseTime: ZonedDateTime) {
    constructor(sendRequestTime: ZonedDateTime, dateTimeProvider: DateTimeProvider)
    : this(sendRequestTime, dateTimeProvider.get(), dateTimeProvider.get())
}