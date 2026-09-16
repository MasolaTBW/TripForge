cat > README.md << 'EOF'
# TripForge

TripForge is a taxi-association courier system that lets customers search taxi routes, create package bookings, and track the status of their deliveries.

## Project Structure

- **/backend** - FastAPI backend for routes, bookings, and tracking logic
- **/frontend** - Vue 3 app for route browsing and booking
- **/docs** - Project documentation

## Stack

- Backend: Python + FastAPI + Poetry
- Frontend: Vue 3 + Vite

## Getting Started

### 1) Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

API docs will be available at:
- http://127.0.0.1:8000/docs

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Then open:
- http://localhost:5173

## Included Features

- Taxi route listing with travel time, fare, and operating hours
- Package booking form with sender and receiver details
- Booking ticket creation with tracking status
- Booking status updates via API
- Vue interface for basic route and booking management

## Notes

This is a working first version based on your taxi-association courier idea. It is designed to be extended with:
- SMS/email notifications
- QR code tracking links
- association approval flow
- customer and receiver notification logic
- persistent database storage
EOF
