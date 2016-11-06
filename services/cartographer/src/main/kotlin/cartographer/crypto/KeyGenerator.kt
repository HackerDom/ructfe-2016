package cartographer.crypto

import java.security.Key

interface KeyGenerator {
    fun generate(): Key
}