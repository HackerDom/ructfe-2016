package cartographer.controllers

import cartographer.data.SynchronizeTimeRequest
import cartographer.data.SynchronizeTimeResponse
import cartographer.providers.DateTimeProvider
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.time.ZoneOffset
import java.time.ZonedDateTime

@RestController
class SynchronizeTimeController(val dateTimeProvider: DateTimeProvider) {

    @RequestMapping("/timesync")
    fun HandleRequest(@RequestBody request: SynchronizeTimeRequest): SynchronizeTimeResponse {
        return SynchronizeTimeResponse(request.sendRequestTime, dateTimeProvider)
    }
}