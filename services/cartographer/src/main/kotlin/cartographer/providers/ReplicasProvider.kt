package cartographer.providers

import cartographer.data.Replica

interface ReplicasProvider {
    fun GetReplicas() : Collection<Replica>
}