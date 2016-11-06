package cartographer.providers

import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import org.springframework.stereotype.Component
import java.net.InetAddress

@Component
class AllPossibleAddressedProvider : AddressedProvider {
    companion object {
        val maxTeamNumberSetting = IntSetting("addresses_provider.max_team_number", 500)
    }

    val maxTeamNumber: Int

    constructor(settingsContainer: SettingsContainer) {
        maxTeamNumber = maxTeamNumberSetting.getValue(settingsContainer)
    }

    override fun getAddresses(): List<InetAddress> {
        return (0..maxTeamNumber).map {
            no -> makeInetAddress(no)
        }
    }

    private fun makeInetAddress(no: Int): InetAddress {
        // TODO: Implement
        throw NotImplementedError()
    }
}