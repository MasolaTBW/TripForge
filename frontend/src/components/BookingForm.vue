<template>
  <section class="booking-panel">
    <h2>Book a package</h2>
    <p v-if="selectedRank" class="selected-rank">Pickup selected: {{ selectedRank.name }}</p>
    <form @submit.prevent="submit">
      <label>Sender name<input v-model="form.sender_name" required /></label>
      <label>Sender phone<input v-model="form.sender_phone" required /></label>
      <label>Sender email<input v-model="form.sender_email" type="email" placeholder="sender@example.com" required /></label>
      <label>Receiver name<input v-model="form.receiver_name" required /></label>
      <label>Receiver phone<input v-model="form.receiver_phone" type="tel" required /></label>
      <label>Receiver email<input v-model="form.receiver_email" type="email" placeholder="receiver@example.com" required /></label>
      <label>Pickup location<select v-model.number="form.pickup_rank_id" required><option :value="null" disabled>Select pickup taxi rank</option><option v-for="rank in ranks" :key="rank.id" :value="rank.id">{{ rank.name }} ({{ rank.city }})</option></select></label>
      <label>Destination<select v-model.number="destinationRankId" @change="selectDestination" required><option :value="null" disabled>Select destination taxi rank</option><option v-for="rank in availableDestinationRanks" :key="rank.id" :value="rank.id">{{ rank.name }} ({{ rank.city }})</option></select></label>
      <label>Package description<textarea v-model="form.package_description" required></textarea></label>
      <label>Estimated package weight (kg)<input v-model.number="form.package_weight_kg" type="number" min="0.1" max="30" placeholder="Enter estimated weight" required /></label>
      <label>Pickup time<input v-model="form.estimated_pickup_time" type="datetime-local" required /></label>
      <button type="submit" :disabled="submitting">{{ submitting ? 'Creating booking...' : 'Create booking' }}</button>
    </form>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  routes: { type: Array, required: true },
  ranks: { type: Array, required: true },
  selectedRank: { type: Object, default: null },
})
const emit = defineEmits(['submit', 'destination-change'])
const submitting = ref(false)
const form = reactive({ sender_name: '', sender_phone: '', sender_email: '', receiver_name: '', receiver_phone: '', receiver_email: '', route_id: null, package_description: '', package_weight_kg: 1, estimated_pickup_time: '2026-09-17T08:30', pickup_rank_id: null })
const destinationRankId = ref(null)
const availableDestinationRanks = computed(() => props.ranks.filter((rank) => rank.id !== form.pickup_rank_id))

watch(() => props.selectedRank, (rank) => {
  if (rank) form.pickup_rank_id = rank.id
})
watch(() => form.pickup_rank_id, (pickupRankId, previousPickupRankId) => {
  if (pickupRankId !== previousPickupRankId) destinationRankId.value = null
  updateRoute()
})

function selectDestination() {
  emit('destination-change', destinationRankId.value)
  updateRoute()
}

function updateRoute() {
  const pickup = props.ranks.find((rank) => rank.id === form.pickup_rank_id)
  const destination = props.ranks.find((rank) => rank.id === destinationRankId.value)
  const matchingRoute = props.routes.find((route) =>
    route.origin.toLowerCase() === pickup?.name.toLowerCase() &&
    route.destination.toLowerCase() === destination?.name.toLowerCase()
  )
  form.route_id = matchingRoute?.id || null
}

async function submit() {
  submitting.value = true
  try { await emit('submit', { ...form, estimated_pickup_time: `${form.estimated_pickup_time}:00` }) } finally { submitting.value = false }
}
</script>

<style scoped>
.booking-panel { padding: 20px; }
h2 { margin-top: 0; }
.selected-rank { padding: 10px 12px; border-left: 3px solid #79b8ff; background: #172033; color: #d3d9e7; }
form { display: grid; gap: 14px; }
label { display: grid; gap: 6px; }
input, select, textarea, button { font: inherit; border: 1px solid #3a495f; border-radius: 8px; padding: 10px 12px; }
textarea { min-height: 90px; resize: vertical; }
button { border: 0; background: #2d7ff9; color: white; font-weight: 700; cursor: pointer; }
button:disabled { cursor: wait; opacity: 0.7; }
</style>
