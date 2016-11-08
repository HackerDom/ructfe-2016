package cartographer.providers

import cartographer.data.Replica
import cartographer.helpers.PeriodicalAction
import cartographer.settings.DurationSetting
import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import org.apache.logging.log4j.LogManager
import org.springframework.stereotype.Component
import java.net.InetAddress
import java.time.Duration
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@Component
class ClosestReplicasProvider : ReplicasProvider {
    companion object {
        private val maxAllowedLatencySetting = DurationSetting("replicas_provider.max_latency", Duration.ofSeconds(1))
        private val replicasUpdatePeriodSetting = DurationSetting("replicas_provider.update_period", Duration.ofMinutes(1))
        private val threadPoolSize = IntSetting("replicas_provider.thread_pool_size", 30)

        private val logger = LogManager.getFormatterLogger()

        private fun updateReplicas(latencyCalculator: LatencyCalculator,
                           executorService: ExecutorService,
                           addressedProvider: AddressedProvider,
                           maxAllowedLatency: Duration): List<Replica> {

            logger.debug("Updating replicas list")

            val closestReplicas = addressedProvider.getAddresses()
                    .map {
                        addr ->
                        Pair(addr, executorService.submit({
                            latencyCalculator.CalcLatency(addr)
                        }))
                    }
                    .filter { pair -> pair.second.get() != null }
                    .filter { pair -> maxAllowedLatency > pair.second.get() as Duration }
                    .map { pair -> Replica(pair.first) }

            logger.debug("New closest replicas list: " +
                    closestReplicas.joinToString { replica -> replica.address.toString() })

            return closestReplicas
        }
    }

    private val updateReplicasAction: PeriodicalAction

    private var closestReplicas = emptyList<Replica>()

    constructor(dateTimeProvider: DateTimeProvider,
                latencyCalculator: LatencyCalculator,
                addressedProvider: AddressedProvider,
                settingsContainer: SettingsContainer) {
        val maxAllowedLatency = maxAllowedLatencySetting.getValue(settingsContainer)
        val replicasUpdatePeriod = replicasUpdatePeriodSetting.getValue(settingsContainer)
        val executorService = Executors.newFixedThreadPool(threadPoolSize.getValue(settingsContainer))

        updateReplicasAction = PeriodicalAction(replicasUpdatePeriod, dateTimeProvider) {
            closestReplicas = updateReplicas(latencyCalculator, executorService, addressedProvider, maxAllowedLatency)
        }
    }

    override fun GetReplicas(): List<Replica> {
        return closestReplicas
    }
}

