package cartographer.providers

import cartographer.data.Replica
import cartographer.helpers.PeriodicalAction
import cartographer.settings.DurationSetting
import cartographer.settings.IntSetting
import cartographer.settings.SettingsContainer
import org.apache.logging.log4j.LogManager
import org.springframework.stereotype.Component
import java.time.Duration
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@Component
class ClosestReplicasProvider : ReplicasProvider {
    companion object {
        private val maxAllowedLatencySetting = DurationSetting("replicas_provider.max_latency", Duration.ofSeconds(10))
        private val replicasUpdatePeriodSetting = DurationSetting("replicas_provider.update_period", Duration.ofMinutes(1))
        private val threadPoolSizeSetting = IntSetting("replicas_provider.thread_pool_size", 2)
        private val replicaSetSizeSetting = IntSetting("replicas_provider.replica_set_size", 10)

        private val logger = LogManager.getFormatterLogger()

        private fun updateReplicas(latencyCalculator: LatencyCalculator,
                           executorService: ExecutorService,
                           addressedProvider: AddressedProvider,
                           maxAllowedLatency: Duration): List<Replica> {

            logger.debug("Updating replicas list")

            val futures = addressedProvider.getAddresses()
                    .map {
                        addr ->
                        Pair(addr, executorService.submit<Long?>({
                            latencyCalculator.CalcLatency(addr, maxAllowedLatency)
                        }))
                    }
                    .toList();
            val closestReplicas = futures
                    .filter {
                        pair ->
                            val latencyMillis = pair.second.get()
                            latencyMillis != null && maxAllowedLatency > Duration.ofMillis(latencyMillis)
                    }
                    .sortedBy { pair -> pair.second.get() }
                    .map { pair -> Replica(pair.first) }

            logger.debug("New closest replicas list: " +
                    closestReplicas.joinToString { replica -> replica.address.toString() })

            return closestReplicas
        }
    }

    private val updateReplicasAction: PeriodicalAction
    private val replicaSetSize: Int

    @Volatile
    private var closestReplicas = emptyList<Replica>()

    constructor(dateTimeProvider: DateTimeProvider,
                latencyCalculator: LatencyCalculator,
                addressedProvider: AddressedProvider,
                settingsContainer: SettingsContainer) {
        val maxAllowedLatency = maxAllowedLatencySetting.getValue(settingsContainer)
        val replicasUpdatePeriod = replicasUpdatePeriodSetting.getValue(settingsContainer)
        val executorService = Executors.newFixedThreadPool(threadPoolSizeSetting.getValue(settingsContainer))

        replicaSetSize = replicaSetSizeSetting.getValue(settingsContainer)
        updateReplicasAction = PeriodicalAction(replicasUpdatePeriod, dateTimeProvider) {
            closestReplicas = updateReplicas(latencyCalculator, executorService, addressedProvider, maxAllowedLatency)
        }
    }

    override fun GetReplicas(): Collection<Replica> {
        if (closestReplicas.size <= replicaSetSize) {
            return closestReplicas
        }

        val top = closestReplicas.subList(0, replicaSetSize / 2)
        val random = Random()
        val low = closestReplicas
                .subList(replicaSetSize / 2, closestReplicas.size)
                .sortedBy { r -> random.nextInt() }
                .subList(0, replicaSetSize / 2)

        return listOf(*top.toTypedArray(), *low.toTypedArray())
    }
}

