package cartographer.providers

import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import org.springframework.stereotype.Component
import java.net.InetAddress
import java.net.InetSocketAddress

@Component
class AllPossibleAddressedProvider : AddressedProvider {
    companion object {
        private val maxTeamNumberSetting = IntSetting("addresses_provider.max_team_number", 1023)
        private val targetPortSetting = IntSetting("addresses_provider.target_port", 80)
    }

    private val maxTeamNumber: Int
    private val targetPort: Int

    constructor(settingsContainer: SettingsContainer) {
        maxTeamNumber = maxTeamNumberSetting.getValue(settingsContainer)
        targetPort = targetPortSetting.getValue(settingsContainer)
    }

    override fun getAddresses(): List<InetSocketAddress> {
        return (0..maxTeamNumber)
            .map {
                no -> makeInetAddress(no)
            }
            .filter {
                address -> address != null
            }
            .map {
                address -> InetSocketAddress(address, targetPort)
            }
            .filter {
                address -> !address.address.isLoopbackAddress
            }
    }

    private fun makeInetAddress(no: Int): InetAddress? {
        try {
            return InetAddress.getByName("cartographer.team$no.ructfe.org")
        } catch (t: Throwable) {
            return null
        }
    }
}