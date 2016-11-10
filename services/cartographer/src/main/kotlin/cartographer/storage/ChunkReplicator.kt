package cartographer.storage

import cartographer.data.Replica
import java.util.*

interface ChunkReplicator {
    fun replicate(id: UUID, chunk: ByteArray, replicas: Collection<Replica>)
}