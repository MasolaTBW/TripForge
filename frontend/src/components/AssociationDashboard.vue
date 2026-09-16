<template>
  <section class="dashboard">
    <div class="dashboard-header"><h2>Association dashboard</h2><button @click="$emit('logout')">Logout</button></div>
    <table>
      <thead><tr><th>Ticket</th><th>Route</th><th>Sender</th><th>Status</th></tr></thead>
      <tbody><tr v-for="booking in bookings" :key="booking.id"><td>{{ booking.ticket_number }}</td><td>{{ routeName(booking.route_id) }}</td><td>{{ booking.sender_name }}</td><td><select :value="booking.status" @change="$emit('status-change', booking.id, $event.target.value)"><option v-for="status in statuses" :key="status" :value="status">{{ status }}</option></select></td></tr></tbody>
    </table>
  </section>
</template>

<script setup>
defineEmits(['logout', 'status-change'])
const props = defineProps({ bookings: { type: Array, required: true }, routes: { type: Array, required: true } })
const statuses = ['pending', 'accepted', 'declined', 'received', 'in_transit', 'delivered', 'closed']
function routeName(routeId) { const route = props.routes.find((item) => item.id === routeId); return route ? `${route.origin} → ${route.destination}` : 'Unknown' }
</script>

<style scoped>
.dashboard { padding: 20px; background: #111827; border: 1px solid #2a3447; border-radius: 16px; overflow-x: auto; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
button { padding: 10px 14px; border: 0; border-radius: 8px; background: #2d7ff9; color: white; font-weight: 700; cursor: pointer; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 8px; border-bottom: 1px solid #2a3447; text-align: left; white-space: nowrap; }
select { padding: 8px; border-radius: 8px; }
</style>
