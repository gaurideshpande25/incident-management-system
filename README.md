# 🚨 Incident Management System (IMS)

## ArchitectureSignals → FastAPI (Rate Limited) → In-Memory Buffer (deque)
↓ (Debounce Worker)
┌──────────────────────────┐
│   PostgreSQL (Work Items)  │
│   MongoDB (Raw Signals)    │
│   Redis (Dashboard Cache)  │
└──────────────────────────┘
↓
React Dashboard (Live Feed)## Tech Stack
| Layer | Technology | Why |
|-------|-----------|-----|
| API | FastAPI + Python | Async, fast, type-safe |
| Persistence | PostgreSQL | Transactional Work Items + RCA |
| Data Lake | MongoDB | Flexible raw signal storage |
| Cache | Redis | Sub-ms dashboard reads |
| Frontend | React + TypeScript | Reactive UI |
| Deploy | Docker Compose | Single command startup |

## Setup (Docker)
```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Health: http://localhost:8000/api/health

## Seed Data
```bash
chmod +x docs/seed.sh && ./docs/seed.sh
```

## Backpressure Handling
Signals are ingested into an **in-memory `deque(maxlen=100_000)`** before persistence. If the DB is slow or down, signals accumulate in memory rather than crashing the API. The background worker drains the buffer in batches of 500 every 100ms.

## Design Patterns Used
- **Strategy Pattern** — `AlertStrategy` (P0/P1/P2/P3 alerting)
- **State Pattern** — `WorkItemState` (OPEN→INVESTIGATING→RESOLVED→CLOSED)

## Running Tests
```bash
cd backend && pip install -r requirements.txt && pytest tests/
```# incident-management-system
Mission-Critical Incident Management System
