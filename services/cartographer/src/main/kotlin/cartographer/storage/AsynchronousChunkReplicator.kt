package cartographer.storage

import cartographer.data.Replica
import org.springframework.stereotype.Component
import java.util.*

@Component
class AsynchronousChunkReplicator : ChunkReplicator {
    override fun replicate(id: UUID, chunk: ByteArray, replicas: List<Replica>) {
        // TODO: Implement
    }
}