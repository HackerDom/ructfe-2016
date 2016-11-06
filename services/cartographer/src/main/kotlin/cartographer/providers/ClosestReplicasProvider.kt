package cartographer.providers

import cartographer.data.Replica
import cartographer.helpers.PeriodicalAction
import cartographer.settings.DurationSetting
import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import java.net.InetAddress
import java.time.Duration
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class ClosestReplicasProvider : ReplicasProvider {
    companion object {
        val maxAllowedLatencySetting = DurationSetting("replicas_provider.max_latency", Duration.ofSeconds(1))
        val replicasUpdatePeriodSetting = DurationSetting("replicas_provider.update_period", Duration.ofMinutes(1))
        val threadPoolSize = IntSetting("replicas_provider.thread_pool_size", 10)

        fun updateReplicas(latencyCalculator: LatencyCalculator,
                           executorService: ExecutorService,
                           addressedProvider: AddressedProvider,
                           maxAllowedLatency: Duration): List<Replica> {

            val closestReplicas = addressedProvider.getAddresses()
                    .map {
                        addr -> executorService.submit({
                            Pair(addr, latencyCalculator.CalcLatency(addr, maxAllowedLatency))
                        })
                    }
                    .filter { future -> maxAllowedLatency > (future.get() as Pair<*, *>).second as Duration }
                    .map { future -> (future.get() as Pair<*, *>).first as InetAddress }
                    .map(::Replica)

            return closestReplicas
        }
    }

    private val updateReplicasAction: PeriodicalAction

    private var closestReplicas = emptyList<Replica>()

    constructor(latencyCalculator: LatencyCalculator,
                addressedProvider: AddressedProvider,
                settingsContainer: SettingsContainer) {
        val maxAllowedLatency = maxAllowedLatencySetting.getValue(settingsContainer)
        val replicasUpdatePeriod = replicasUpdatePeriodSetting.getValue(settingsContainer)
        val executorService = Executors.newFixedThreadPool(threadPoolSize.getValue(settingsContainer))

        updateReplicasAction = PeriodicalAction(replicasUpdatePeriod) {
            closestReplicas = updateReplicas(latencyCalculator, executorService, addressedProvider, maxAllowedLatency)
        }
    }

    override fun GetReplicas(): List<Replica> {
        return closestReplicas
    }
}

