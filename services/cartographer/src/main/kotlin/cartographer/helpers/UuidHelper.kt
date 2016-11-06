package cartographer.helpers

import java.util.*


fun parseUuidSafe(idString: String?): UUID? {
    try {
        if (idString == null) {
            return null
        }

        return UUID.fromString(idString)
    } catch (t: Throwable) {
        return null
    }
}
