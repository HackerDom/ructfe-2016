package cartographer.providers

import java.net.InetSocketAddress

interface AddressedProvider {
    fun getAddresses() : List<InetSocketAddress>
}