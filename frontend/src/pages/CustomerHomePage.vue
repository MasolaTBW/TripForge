<template>
  <main class="customer-page">
    <div class="page-heading">
      <div><span class="eyebrow">TripForge Courier</span><h1>Send packages with your local taxi network</h1><p>Search a taxi rank, choose a route, and create a booking in minutes.</p></div>
    </div>
    <div class="customer-grid">
      <TaxiRankMap :ranks="taxiRanks" :selected-rank="selectedRank" :destination-rank="destinationRank" @select="selectRank" />
      <section class="booking-column">
        <p v-if="error" class="api-error">Unable to load routes. Check that the backend is running on {{ apiBaseUrl }}.</p>
        <p v-else-if="!routes.length" class="loading-message">Loading routes...</p>
        <BookingForm v-else :routes="routes" :ranks="taxiRanks" :selected-rank="selectedRank" @destination-change="selectDestination" @submit="submitBooking" />
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import BookingForm from '../components/BookingForm.vue'
import TaxiRankMap from '../components/TaxiRankMap.vue'
import { useTripForgeApi } from '../composables/useTripForgeApi.js'

const { routes, taxiRanks, error, fetchRoutes, fetchTaxiRanks, createBooking } = useTripForgeApi()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const selectedRank = ref(null)
const selectedDestinationRankId = ref(null)
const destinationRank = computed(() => {
  return taxiRanks.value.find((rank) => rank.id === selectedDestinationRankId.value) || null
})

function selectRank(rank) { selectedRank.value = rank }
function selectDestination(rankId) { selectedDestinationRankId.value = rankId }
async function submitBooking(booking) {
  await createBooking(booking)
  window.alert('Booking created successfully.')
}

onMounted(async () => {
  await Promise.all([fetchRoutes(), fetchTaxiRanks()])
})
</script>

<style scoped>
.customer-page { display: grid; gap: 24px; }
.page-heading { padding: 10px 0; }
.eyebrow { color: #79b8ff; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
h1 { max-width: 760px; margin: 8px 0; font-size: clamp(2rem, 5vw, 4.2rem); line-height: 1; }
p { color: #c5d2e5; }
.customer-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; }
.customer-grid > * { background: #111827; border: 1px solid #2a3447; border-radius: 16px; }
.booking-column { min-width: 0; }
.loading-message, .api-error { margin: 0; padding: 20px; }
.api-error { color: #ff8686; }
@media (max-width: 900px) { .customer-grid { grid-template-columns: 1fr; } }
</style>
