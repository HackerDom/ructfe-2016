package cartographer.controllers

import cartographer.configs.CryptographyConfig
import cartographer.crypto.ChunkCryptography
import cartographer.crypto.KeyGenerator
import cartographer.crypto.KeyStorage
import cartographer.data.DecryptImageRequest
import cartographer.data.EncryptImageResponse
import cartographer.helpers.parseUuidSafe
import cartographer.helpers.throttle
import cartographer.providers.ReplicasProvider
import cartographer.storage.ChunkReplicator
import cartographer.storage.ChunkStorage
import cartographer.throttling.Throttler
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.RestController
import java.util.*
import javax.crypto.spec.SecretKeySpec

@RestController
class ImagesController(val chunkStorage: ChunkStorage,
                       val keyGenerator: KeyGenerator,
                       val masterKeyStorage: KeyStorage,
                       val chunkCryptography: ChunkCryptography,
                       val throttler: Throttler,
                       val replicasProvider: ReplicasProvider,
                       val chunkReplicator: ChunkReplicator) {
    @RequestMapping("/images/encrypt", method = arrayOf(RequestMethod.POST))
    fun EncryptImage(@RequestBody image: ByteArray): ResponseEntity<EncryptImageResponse> {
        return throttle(throttler) {
            val id = UUID.randomUUID()
            val sessionKey = keyGenerator.generate()
            val masterKey = masterKeyStorage.get()

            val chunk = chunkCryptography.encrypt(sessionKey, masterKey, image)
            chunkStorage.putChunk(id, chunk)

            val replicas = replicasProvider.GetReplicas()
            chunkReplicator.replicate(id, chunk, replicas)

            return ResponseEntity.ok(EncryptImageResponse(id.toString(), sessionKey.encoded, replicas))
        }
    }

    @RequestMapping("/images/encrypt", method = arrayOf(RequestMethod.POST))
    fun DencryptImage(@RequestBody request: DecryptImageRequest): ResponseEntity<ByteArray> {
        return throttle(throttler) {
            val id = parseUuidSafe(request.id)
            if (id == null && request.chunk == null) {
                return ResponseEntity(HttpStatus.BAD_REQUEST)
            }

            val chunk = request.chunk ?: chunkStorage.getChunk(id!!) ?: return ResponseEntity(HttpStatus.NOT_FOUND)

            val sessionKey = SecretKeySpec(request.key, CryptographyConfig.keySpec)
            val masterKey = masterKeyStorage.get()
            return ResponseEntity.ok(chunkCryptography.decrypt(sessionKey, masterKey, chunk))
        }
    }
}
