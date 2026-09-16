<template>
  <div class="app-shell">
    <header class="topbar">
      <div><strong>TripForge</strong><span>Courier network</span></div>
      <button v-if="isLoggedIn" class="session-button" @click="logout">Association logout</button>
      <button v-else class="session-button" @click="showLogin = !showLogin">Association login</button>
    </header>

    <CustomerHomePage />

    <section v-if="showLogin && !isLoggedIn" class="login-panel">
      <h2>Association login</h2>
      <form @submit.prevent="loginAssociation">
        <input v-model="loginForm.email" type="email" placeholder="admin@gmail.com" required />
        <input v-model="loginForm.password" type="password" placeholder="admin123" required />
        <button type="submit" :disabled="loginBusy">{{ loginBusy ? 'Signing in...' : 'Login' }}</button>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </form>
    </section>

    <AssociationDashboard v-if="isLoggedIn" :bookings="bookings" :routes="routes" @logout="logout" @status-change="updateStatus" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import AssociationDashboard from './components/AssociationDashboard.vue'
import CustomerHomePage from './pages/CustomerHomePage.vue'
import { useTripForgeApi } from './composables/useTripForgeApi.js'

const { routes, bookings, fetchRoutes, fetchBookings, loginAssociation: authenticate, updateBookingStatus } = useTripForgeApi()
const showLogin = ref(false)
const isLoggedIn = ref(false)
const loginError = ref('')
const loginBusy = ref(false)
const loginForm = reactive({ email: 'admin@gmail.com', password: 'admin123' })

async function loginAssociation() {
  loginError.value = ''
  loginBusy.value = true
  try {
    const result = await authenticate(loginForm)
    if (!result.ok) {
      loginError.value = result.message
      return
    }
    isLoggedIn.value = true
    showLogin.value = false
    await fetchBookings()
  } catch {
    loginError.value = 'Login succeeded, but the dashboard data could not be loaded.'
  } finally {
    loginBusy.value = false
  }
}

function logout() { isLoggedIn.value = false }
async function updateStatus(bookingId, status) { await updateBookingStatus(bookingId, status); await fetchBookings() }

onMounted(fetchRoutes)
</script>

<style>
:root { font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #e6edf3; background: #0d1321; }
* { box-sizing: border-box; }
body { margin: 0; min-width: 320px; }
button, input, select, textarea { font: inherit; }
.app-shell { max-width: 1400px; margin: 0 auto; padding: 28px 20px 60px; }
.topbar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 30px; }
.topbar div { display: grid; gap: 3px; }
.topbar strong { font-size: 1.25rem; }
.topbar span { color: #9baac0; font-size: 0.85rem; }
.session-button { width: auto; padding: 10px 14px; border: 1px solid #3a495f; border-radius: 8px; background: #172033; color: white; cursor: pointer; }
.login-panel { max-width: 420px; margin-top: 24px; padding: 20px; border: 1px solid #2a3447; border-radius: 16px; background: #111827; }
.login-panel form { display: grid; gap: 12px; }
.login-panel input { padding: 10px 12px; border: 1px solid #3a495f; border-radius: 8px; background: #0d1321; color: white; }
.login-panel button { padding: 10px 12px; border: 0; border-radius: 8px; background: #2d7ff9; color: white; font-weight: 700; cursor: pointer; }
.login-panel button:disabled { cursor: wait; opacity: 0.7; }
.error { color: #ff8686; }
</style>
