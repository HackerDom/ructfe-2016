package cartographer.data

import com.fasterxml.jackson.annotation.JsonProperty
import java.net.InetSocketAddress

data class Replica(@JsonProperty("address") val address: InetSocketAddress)