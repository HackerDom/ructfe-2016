package cartographer.crypto

import java.security.Key

interface KeyStorage {
    fun get(): Key
}