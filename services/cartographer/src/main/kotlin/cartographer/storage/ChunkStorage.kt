package cartographer.storage

import java.util.*

interface ChunkStorage {
    fun getChunk(id: UUID): ByteArray?

    fun putChunk(id: UUID, chunk: ByteArray): Boolean
}