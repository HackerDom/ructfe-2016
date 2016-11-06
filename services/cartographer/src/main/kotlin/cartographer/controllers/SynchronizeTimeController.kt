package cartographer.controllers

import cartographer.data.SynchronizeTimeRequest
import cartographer.data.SynchronizeTimeResponse
import cartographer.helpers.throttle
import cartographer.providers.DateTimeProvider
import cartographer.throttling.Throttler
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.RestController

@RestController
class SynchronizeTimeController(val dateTimeProvider: DateTimeProvider, val throttler: Throttler) {
    @RequestMapping("/timesync", method = arrayOf(RequestMethod.POST))
    fun HandleRequest(@RequestBody request: SynchronizeTimeRequest): ResponseEntity<SynchronizeTimeResponse> {
        return throttle(throttler) {
            return ResponseEntity.ok(SynchronizeTimeResponse(request.sendRequestTime, dateTimeProvider))
        }
    }
}