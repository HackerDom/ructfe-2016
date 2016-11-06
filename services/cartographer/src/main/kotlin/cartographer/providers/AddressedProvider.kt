package cartographer.providers

import java.net.InetAddress

interface AddressedProvider {
    fun getAddresses() : List<InetAddress>
}