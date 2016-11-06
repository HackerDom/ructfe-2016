package cartographer.data

import com.fasterxml.jackson.annotation.JsonProperty
import java.net.InetAddress

data class Replica(@JsonProperty("address") val address: InetAddress)