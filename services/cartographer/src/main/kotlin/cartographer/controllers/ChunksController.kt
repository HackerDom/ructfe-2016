package cartographer.controllers

import cartographer.helpers.parseUuidSafe
import cartographer.storage.ChunkStorage
import cartographer.throttling.Throttler
import cartographer.helpers.throttle
import org.springframework.http.HttpStatus
import org.springframework.http.RequestEntity
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.RestController
import java.util.*

@RestController
class ChunksController(val chunkStorage: ChunkStorage, val throttler: Throttler) {
    @RequestMapping("/chunks/{idString}", method = arrayOf(RequestMethod.GET))
    fun GetChunk(@PathVariable("idString") idString: String): ResponseEntity<ByteArray> {
        return throttle(throttler) {
            val id = parseUuidSafe(idString) ?: return ResponseEntity(HttpStatus.BAD_REQUEST)
            val chunk = chunkStorage.getChunk(id)
            return if (chunk != null) ResponseEntity(chunk, HttpStatus.OK) else ResponseEntity(HttpStatus.NOT_FOUND)
        }
    }

    @RequestMapping("/chunks/{idString}", method = arrayOf(RequestMethod.PUT))
    fun PutChunk(@PathVariable("idString") idString: String, chunk: RequestEntity<ByteArray>)
            : ResponseEntity<ByteArray> {
        return throttle(throttler) {
            val id = parseUuidSafe(idString) ?: return ResponseEntity(HttpStatus.BAD_REQUEST)
            return if (chunkStorage.putChunk(id, chunk.body)) ResponseEntity(HttpStatus.OK)
            else ResponseEntity(HttpStatus.CONFLICT)
        }
    }
}