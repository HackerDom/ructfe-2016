package cartographer.helpers

import java.nio.ByteBuffer
import java.util.*

fun bytesToInt(bytes: ByteArray): Int {
    return ByteBuffer.wrap(bytes).int
}

fun intToBytes(size: Int): ByteArray {
    return ByteBuffer.allocate(4).putInt(size).array()
}

fun bytesToUuid(bytes: ByteArray): UUID {
    val byteBuffer = ByteBuffer.wrap(bytes)
    return UUID(byteBuffer.long, byteBuffer.long)
}

fun uuidToBytes(uuid: UUID): ByteArray {
    return ByteBuffer.allocate(16)
            .putLong(uuid.mostSignificantBits)
            .putLong(uuid.leastSignificantBits)
            .array()
}