import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

L.Marker.prototype.options.icon = defaultIcon

export function setupMap(container, taxiRanks) {
  const map = L.map(container).setView([-25.7479, 28.2293], 11)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map)

  map.rankMarkers = L.layerGroup().addTo(map)
  setRankMarkers(map, taxiRanks)

  return map
}

export function setRankMarkers(map, taxiRanks) {
  map.rankMarkers.clearLayers()
  taxiRanks.forEach((rank) => {
    const marker = L.marker([rank.lat, rank.lng]).addTo(map.rankMarkers)
    marker.bindPopup(`<strong>${rank.name}</strong><br>${rank.city}<br>Open: ${rank.hours}`)
  })
}

export async function drawRoute(map, pickupRank, destinationRank) {
  if (!pickupRank || !destinationRank) return null

  const response = await fetch(
    `https://router.project-osrm.org/route/v1/driving/${pickupRank.lng},${pickupRank.lat};${destinationRank.lng},${destinationRank.lat}?overview=full&geometries=geojson`,
  )
  if (!response.ok) throw new Error('Unable to calculate route')

  const payload = await response.json()
  const route = payload.routes?.[0]
  if (!route) throw new Error('No route found')

  const layer = L.geoJSON(route.geometry, {
    style: { color: '#2d7ff9', weight: 5, opacity: 0.85 },
  }).addTo(map)
  map.fitBounds(layer.getBounds(), { padding: [30, 30] })

  return {
    layer,
    distanceKm: route.distance / 1000,
    durationMinutes: Math.round(route.duration / 60),
  }
}
