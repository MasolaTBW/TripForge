import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function useTripForgeApi() {
  const routes = ref([])
  const taxiRanks = ref([])
  const bookings = ref([])
  const error = ref('')

  async function fetchRoutes() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/routes`)
      if (!response.ok) throw new Error(`Route request failed (${response.status})`)
      routes.value = await response.json()
      error.value = ''
      return routes.value
    } catch (requestError) {
      error.value = requestError.message
      throw requestError
    }
  }

  async function fetchTaxiRanks() {
    const response = await fetch(`${API_BASE_URL}/api/taxi-ranks`)
    if (!response.ok) throw new Error(`Taxi-rank request failed (${response.status})`)
    taxiRanks.value = (await response.json()).map((rank) => ({
      ...rank,
      lat: rank.latitude,
      lng: rank.longitude,
      hours: rank.operating_hours,
    }))
    return taxiRanks.value
  }

  async function fetchBookings() {
    const response = await fetch(`${API_BASE_URL}/api/bookings`)
    if (!response.ok) throw new Error('Unable to load bookings')
    bookings.value = await response.json()
    return bookings.value
  }

  async function loginAssociation(credentials) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/association/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      })
      return { ok: response.ok, message: response.ok ? '' : 'Invalid association email or password.' }
    } catch {
      return { ok: false, message: `Cannot reach the backend at ${API_BASE_URL}.` }
    }
  }

  async function createBooking(booking) {
    const response = await fetch(`${API_BASE_URL}/api/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(booking),
    })
    if (!response.ok) throw new Error('Unable to create booking')
    return response.json()
  }

  async function updateBookingStatus(bookingId, status) {
    const response = await fetch(`${API_BASE_URL}/api/bookings/${bookingId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    if (!response.ok) throw new Error('Unable to update booking')
    return response.json()
  }

  return {
    routes,
    taxiRanks,
    bookings,
    error,
    fetchRoutes,
    fetchTaxiRanks,
    fetchBookings,
    loginAssociation,
    createBooking,
    updateBookingStatus,
  }
}
