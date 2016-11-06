package cartographer.storage

import cartographer.data.Replica
import java.util.*

// TODO Implement
interface ChunkReplicator {
    fun replicate(id: UUID, chunk: ByteArray, replicas: List<Replica>)
}