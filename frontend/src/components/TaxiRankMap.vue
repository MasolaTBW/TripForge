<template>
  <section class="map-panel">
    <div class="panel-header">
      <div>
        <span class="eyebrow">OpenStreetMap</span>
        <h2>Find a taxi rank</h2>
      </div>
      <input v-model="search" class="search-box" placeholder="Search rank or city" />
    </div>
    <div ref="mapContainer" class="map-container"></div>
    <div v-if="routeLoading" class="route-status">Calculating driving route...</div>
    <div v-else-if="routeError" class="route-status route-error">{{ routeError }}</div>
    <div v-else-if="routeSummary" class="route-summary">
      <strong>{{ routeSummary.distanceKm.toFixed(1) }} km</strong>
      <span>{{ routeSummary.durationMinutes }} min estimated driving time</span>
      <small>{{ selectedRank.name }} to {{ destinationRank.name }}</small>
    </div>
    <div v-else class="route-status">Select both pickup and destination to show distance.</div>
    <div class="rank-list">
      <button v-for="rank in filteredRanks" :key="rank.id" class="rank-card" @click="selectRank(rank)">
        <strong>{{ rank.name }}</strong>
        <span>{{ rank.city }}</span>
        <small>{{ rank.hours }}</small>
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { drawRoute, setRankMarkers, setupMap } from '../leaflet-map.js'

const props = defineProps({
  ranks: { type: Array, required: true },
  selectedRank: { type: Object, default: null },
  destinationRank: { type: Object, default: null },
})

const emit = defineEmits(['select'])
const mapContainer = ref(null)
const search = ref('')
const selectedRank = computed(() => props.selectedRank)
const destinationRank = computed(() => props.destinationRank)
const map = ref(null)
const routeLayer = ref(null)
const routeSummary = ref(null)
const routeLoading = ref(false)
const routeError = ref('')

const filteredRanks = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return props.ranks
  return props.ranks.filter((rank) => `${rank.name} ${rank.city}`.toLowerCase().includes(query))
})

function selectRank(rank) {
  emit('select', rank)
}

onMounted(() => {
  map.value = setupMap(mapContainer.value, props.ranks)
  refreshRoute()
})

watch(() => props.ranks, (ranks) => {
  if (map.value) setRankMarkers(map.value, ranks)
}, { deep: true })

async function refreshRoute() {
  if (map.value) {
    const visibleRanks = props.selectedRank && props.destinationRank
      ? [props.selectedRank, props.destinationRank].filter((rank, index, ranks) => ranks.findIndex((item) => item.id === rank.id) === index)
      : props.ranks
    setRankMarkers(map.value, visibleRanks)
  }
  if (routeLayer.value) {
    map.value.removeLayer(routeLayer.value)
    routeLayer.value = null
  }
  routeSummary.value = null
  routeError.value = ''
  if (!map.value || !props.selectedRank || !props.destinationRank) return

  routeLoading.value = true
  try {
    const result = await drawRoute(map.value, props.selectedRank, props.destinationRank)
    routeLayer.value = result.layer
    routeSummary.value = result
  } catch {
    routeError.value = 'The route could not be calculated right now.'
  } finally {
    routeLoading.value = false
  }
}

watch(
  [() => props.selectedRank?.id, () => props.destinationRank?.id],
  refreshRoute,
  { immediate: true },
)
</script>

<style scoped>
.map-panel { min-height: 700px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }
.eyebrow { color: #79b8ff; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
h2 { margin: 4px 0 0; }
.search-box { width: 220px; }
.map-container { width: 100%; height: 420px; border: 1px solid #36455d; border-radius: 12px; overflow: hidden; }
.route-status, .route-summary { margin-top: 12px; padding: 12px; border-radius: 10px; background: #172033; }
.route-summary { display: grid; gap: 3px; border-left: 3px solid #2d7ff9; }
.route-summary strong { color: #79b8ff; font-size: 1.25rem; }
.route-summary span, .route-summary small { color: #d3d9e7; }
.route-error { color: #ff8686; }
.rank-list { display: grid; gap: 12px; margin-top: 18px; }
.rank-card { display: flex; flex-direction: column; gap: 3px; width: 100%; padding: 12px; border: 1px solid #3a495f; border-radius: 10px; background: #172033; color: white; text-align: left; cursor: pointer; }
.rank-card span, .rank-card small { color: #d3d9e7; }
@media (max-width: 700px) { .panel-header { align-items: flex-start; flex-direction: column; } .search-box { width: 100%; } }
</style>
