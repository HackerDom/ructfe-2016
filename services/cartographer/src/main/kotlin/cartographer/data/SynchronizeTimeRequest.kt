package cartographer.data

import com.fasterxml.jackson.annotation.JsonProperty
import java.time.ZonedDateTime

data class SynchronizeTimeRequest(@JsonProperty("sendRequestTime") val sendRequestTime: ZonedDateTime)