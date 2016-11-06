package cartographer.storage

import org.springframework.stereotype.Component
import java.util.*

// TODO Make persistent
@Component
class InMemoryChunkStorage : ChunkStorage {
    val storage: MutableMap<UUID, ByteArray> = HashMap<UUID, ByteArray>()

    override fun getChunk(id: UUID): ByteArray? {
        return storage[id]
    }

    override fun putChunk(id: UUID, chunk: ByteArray): Boolean {
        return storage.getOrPut(id, { chunk }) == chunk
    }
}