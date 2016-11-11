package cartographer.storage

import cartographer.data.Replica
import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import cartographer.settings.StringSetting
import org.apache.logging.log4j.LogManager
import org.springframework.http.HttpEntity
import org.springframework.http.HttpMethod
import org.springframework.stereotype.Component
import org.springframework.web.client.HttpClientErrorException
import org.springframework.web.client.RestTemplate
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger

@Component
class AsynchronousChunkReplicator : ChunkReplicator {
    companion object {
        private val maxRetriesCountSetting = IntSetting("replicator.retries_count", 3)
        private val threadCountSetting = IntSetting("replicator.threads_count", 5)
        private val chunksEndpointSeting = StringSetting("replicator.chunksEndpoint", "chunks")
        private val maxQueueSizeSetting = IntSetting("replicator.max_queue_size", 100)

        private val logger = LogManager.getFormatterLogger()
    }

    private val maxRetriesCount: Int
    private val executor: ExecutorService
    private val chunksEndpoint: String
    private val queueSize = AtomicInteger()
    private val maxQueueSize: Int

    constructor(settingsContainer: SettingsContainer) {
        maxRetriesCount = maxRetriesCountSetting.getValue(settingsContainer)
        chunksEndpoint = chunksEndpointSeting.getValue(settingsContainer)
        val threadCount = threadCountSetting.getValue(settingsContainer)
        executor = Executors.newFixedThreadPool(threadCount)
        maxQueueSize = maxQueueSizeSetting.getValue(settingsContainer)
    }

    override fun replicate(id: UUID, chunk: ByteArray, replicas: Collection<Replica>) {
        for (replica in replicas) {
            queueSize.incrementAndGet()
            executor.submit { replicateOne(id, chunk, replica) }
        }
    }

    private fun replicateOne(id: UUID, chunk: ByteArray, replica: Replica) {
        val currentQueueSize = queueSize.decrementAndGet()
        if (currentQueueSize >= maxQueueSize) {
            return
        }

        for (attempt in 1..maxRetriesCount) {
            try {
                val uri = "http://${replica.address.hostName}:${replica.address.port}/$chunksEndpoint/$id"

                val rest = RestTemplate()
                val responseEntity = rest.exchange(uri, HttpMethod.PUT, HttpEntity<ByteArray>(chunk), Unit::class.java)

                if (responseEntity.statusCode.is2xxSuccessful) {
                    logger.debug("Successfully put chunk $id to $replica")
                    return
                }
            } catch (ex: HttpClientErrorException) {
                logger.warn("Failed to put chunk $id to $replica after $attempt attempt(s). " +
                        "Status code: ${ex.statusCode}")
            } catch (t: Throwable) {
                logger.warn("Failed to put chunk $id to $replica after $attempt attempt(s). " +
                        "Unhandled exception: ${t}")
            }
        }
    }
}