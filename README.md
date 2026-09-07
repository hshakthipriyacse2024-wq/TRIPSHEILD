# TripShield AI

### Autonomous Travel Recovery & Resilience Platform

> **"Don't just rebook the disrupted service. Protect the entire journey."**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 What is TripShield AI?

TripShield AI transforms a static travel itinerary into a **living Journey Digital Twin** that understands dependencies, predicts ripple effects, and autonomously orchestrates recovery when disruption occurs.

A travel itinerary is not a collection of independent bookings — it's a **dependency network**. When one component is disrupted, the disruption can propagate through the entire journey. TripShield AI understands this and recovers the **entire journey**, not just individual bookings.

### Core Innovation

| Feature | Description |
|---------|-------------|
| **Journey Digital Twin** | Visual graph representation of your trip as interconnected nodes |
| **Ripple Impact Engine** | Calculates cascading effects when any component is disrupted |
| **Recovery Optimization** | Generates multiple recovery strategies scored by your preferences |
| **What-If Simulator** | Simulate disruptions without affecting your real itinerary |
| **TripShield Guardian** | AI assistant that uses your actual trip data to answer questions |
| **Autonomous Recovery** | Configurable auto-recovery with human-in-the-loop approval |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** — [Download](https://python.org)
- **Node.js 18+** — [Download](https://nodejs.org)
- **Git** — [Download](https://git-scm.com)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd tripshield-ai
cp .env.example .env
```

### 2. Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend starts at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend starts at `http://localhost:3000`.

### 4. Run the Demo

1. Open `http://localhost:3000` in your browser
2. Register a new account or use demo credentials
3. Click **"Load Demo Journey"** on the Dashboard
4. Click **"Simulate 4-Hour Delay"** to trigger a disruption
5. Watch the Journey Digital Twin update in real-time
6. Review recovery options and approve the recommended strategy
7. See the itinerary automatically rebuilt

---

## 🏗️ Architecture

```
Frontend (Next.js + React + TypeScript)
        ↓
API Gateway (FastAPI)
        ↓
┌───────┴───────────────────────────────┐
│ Auth │ Journey │ Digital Twin         │
│ Service│ Service │ Service             │
├───────┼─────────┼─────────────────────┤
│ Ripple Impact │ Recovery Optimization │
│ Engine        │ Engine                │
├───────────────┼───────────────────────┤
│ AI Service    │ Provider Layer        │
│ (Guardian)    │ (Mock/Real)           │
├───────────────┴───────────────────────┤
│ Database (SQLite/PostgreSQL)          │
└───────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full system design.

---

## 📁 Project Structure

```
tripshield-ai/
├── frontend/          # Next.js React frontend
│   ├── src/
│   │   ├── app/       # Pages (App Router)
│   │   ├── components/# UI components
│   │   ├── services/  # API client
│   │   ├── store/     # Zustand state management
│   │   ├── types/     # TypeScript types
│   │   └── lib/       # Utilities
│   └── package.json
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── engines/   # Core algorithms
│   │   ├── services/  # Business logic
│   │   ├── providers/ # External integrations
│   │   ├── ai/        # AI/LLM layer
│   │   ├── core/      # Auth & security
│   │   └── seed/      # Demo data
│   └── requirements.txt
├── docker/            # Docker configuration
├── docs/              # Documentation
├── docker-compose.yml
└── .env.example
```

---

## 🧪 Demo Scenarios

| Scenario | Description | Trigger |
|----------|-------------|---------|
| Normal Journey | Chennai → Delhi → Paris, all confirmed | Load Demo Journey |
| 4-Hour Flight Delay | First flight delayed, cascading impact | Simulate Delay |
| Flight Cancellation | First flight cancelled, full reroute needed | Simulate Cancellation |
| What-If Analysis | Simulate any disruption without changing data | What-If Simulator |

---

## 🔐 User Roles

| Role | Access |
|------|--------|
| **Traveler** | Create trips, view digital twin, manage preferences, approve recovery |
| **Ops Admin** | View all journeys, monitor disruptions, override AI decisions, audit logs |
| **Sys Admin** | User management, system config, provider management, full access |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| State | Zustand |
| Visualization | React Flow (graph), Recharts (analytics) |
| Backend | Python 3.11, FastAPI |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose + passlib/bcrypt) |
| AI | Provider-agnostic (MockLLM for demo) |
| Container | Docker + Docker Compose |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture & data flow |
| [API.md](API.md) | Complete API reference |
| [DATABASE.md](DATABASE.md) | Database schema & ER diagram |
| [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) | AI/LLM design & principles |
| [RECOVERY_ENGINE.md](RECOVERY_ENGINE.md) | Recovery optimization algorithm |
| [DIGITAL_TWIN.md](DIGITAL_TWIN.md) | Journey Digital Twin design |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide |
| [DEMO_GUIDE.md](DEMO_GUIDE.md) | Step-by-step demo walkthrough |
| [TESTING.md](TESTING.md) | Testing strategy & guide |

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 🧠 Key Algorithms

### Ripple Impact Score (0-100)
```
Impact = W_time × TimeImpact + W_connection × ConnectionRisk + 
         W_financial × FinancialExposure + W_priority × TravelerPriority + 
         W_criticality × DependencyCriticality
```

### Recovery Score (0-100)
```
Score = w_time × TimeScore + w_cost × CostScore + w_comfort × ComfortScore + 
        w_feasibility × FeasibilityScore + w_preservation × PreservationScore + 
        w_urgency × UrgencyScore
```
Weights are personalized from each traveler's preference profile.

### Resilience Score (0-100)
```
Resilience = f(ConnectionBuffer, AlternativeAvailability, BookingFlexibility,
               DependencyDepth, NonRefundableExposure, RouteRisk)
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Built with ❤️ for resilient travel**
