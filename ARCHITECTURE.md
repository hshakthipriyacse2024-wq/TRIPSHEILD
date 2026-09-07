# TripShield AI — System Architecture

## Overview

TripShield AI follows a modular monolith architecture where services are logically separated but deployed as a single unit. This enables rapid development while maintaining clean boundaries for future microservice extraction.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Dashboard│ │ Journey  │ │ Recovery │ │ Guardian │  ...      │
│  │  Page    │ │  Pages   │ │  Center  │ │   Chat   │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │             │            │             │                │
│  ┌────┴─────────────┴────────────┴─────────────┴──────┐        │
│  │             API Service Layer (axios)               │        │
│  └────────────────────────┬───────────────────────────┘        │
│  ┌────────────────────────┴───────────────────────────┐        │
│  │          State Management (Zustand Stores)          │        │
│  └────────────────────────────────────────────────────┘        │
└───────────────────────────┬────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│  ┌────────────────────────────────────────────────────┐        │
│  │              API Layer (Routes + Validation)        │        │
│  │  ┌──────┐ ┌────────┐ ┌──────────┐ ┌──────────┐   │        │
│  │  │ Auth │ │Journey │ │Disruption│ │ Recovery │    │        │
│  │  │Routes│ │ Routes │ │  Routes  │ │  Routes  │ ...│        │
│  │  └──┬───┘ └───┬────┘ └────┬─────┘ └────┬─────┘   │        │
│  └─────┼─────────┼───────────┼─────────────┼─────────┘        │
│        │         │           │             │                   │
│  ┌─────┼─────────┼───────────┼─────────────┼─────────┐        │
│  │     │    SERVICE LAYER    │             │          │        │
│  │  ┌──┴───┐ ┌───┴────┐ ┌───┴──────┐ ┌───┴──────┐  │        │
│  │  │ Auth │ │Journey │ │ Notif    │ │  Audit   │  │        │
│  │  │ Svc  │ │  Svc   │ │  Svc     │ │   Svc    │  │        │
│  │  └──────┘ └────────┘ └──────────┘ └──────────┘  │        │
│  └──────────────────┬────────────────────────────────┘        │
│                     │                                          │
│  ┌──────────────────┴────────────────────────────────┐        │
│  │              ENGINE LAYER (Core Algorithms)        │        │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐       │        │
│  │  │  Ripple   │ │ Recovery  │ │Resilience │       │        │
│  │  │  Impact   │ │ Optimizer │ │  Scorer   │       │        │
│  │  └───────────┘ └───────────┘ └───────────┘       │        │
│  │  ┌───────────┐ ┌───────────┐                      │        │
│  │  │   Risk    │ │Preference │                      │        │
│  │  │ Assessor  │ │  Engine   │                      │        │
│  │  └───────────┘ └───────────┘                      │        │
│  └──────────────────┬────────────────────────────────┘        │
│                     │                                          │
│  ┌──────────────────┴──────────────┐ ┌──────────────────┐     │
│  │       PROVIDER LAYER            │ │    AI LAYER       │     │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ │ │ ┌──────────────┐ │     │
│  │  │Flight │ │ Hotel │ │Weather│ │ │ │  Guardian     │ │     │
│  │  │(Mock) │ │(Mock) │ │(Mock) │ │ │ │  (MockLLM)   │ │     │
│  │  └───────┘ └───────┘ └───────┘ │ │ │  Explainer   │ │     │
│  │  ┌───────┐ ┌───────┐           │ │ └──────────────┘ │     │
│  │  │Transp.│ │Activ. │           │ │                   │     │
│  │  │(Mock) │ │(Mock) │           │ │                   │     │
│  │  └───────┘ └───────┘           │ │                   │     │
│  └─────────────────────────────────┘ └──────────────────┘     │
│                     │                        │                 │
│  ┌──────────────────┴────────────────────────┴────────┐       │
│  │                  DATA LAYER                         │       │
│  │  ┌─────────────┐    ┌──────────────┐               │       │
│  │  │ SQLAlchemy  │    │   SQLite     │               │       │
│  │  │   ORM       │───▶│ (Dev/Demo)   │               │       │
│  │  │             │    │ PostgreSQL   │               │       │
│  │  │             │    │ (Production) │               │       │
│  │  └─────────────┘    └──────────────┘               │       │
│  └────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Journey Creation Flow
```
User → Frontend → POST /api/v1/journeys → JourneyService → DB
User → Frontend → POST /api/v1/journeys/{id}/nodes → JourneyService → DB
User → Frontend → POST /api/v1/journeys/{id}/dependencies → JourneyService → DB
Frontend → GET /api/v1/journeys/{id}/digital-twin → DigitalTwinService → DB → Graph JSON
Frontend → GET /api/v1/journeys/{id}/resilience-score → ResilienceScorer → Score
```

### 2. Disruption Detection Flow
```
Disruption Event → POST /api/v1/disruptions
    → Create Disruption record
    → RippleImpactEngine.calculate_impact()
        → Build adjacency graph from dependencies
        → BFS traverse downstream nodes
        → Calculate time/location/connection conflicts
        → Score and classify severity
    → Store ImpactAnalysis
    → Update affected node statuses (confirmed → at_risk/affected)
    → Update journey status (active → disrupted)
    → NotificationService.create_disruption_notification()
    → AuditService.log()
    → Return disruption + impact analysis
```

### 3. Recovery Flow
```
POST /api/v1/journeys/{id}/recovery-options
    → Load disruption + impact analysis
    → RecoveryOptimizer.generate_strategies()
        → generate_minimal_recovery()
        → generate_connection_preserving()
        → generate_cost_optimized()
        → generate_comfort_optimized()
        → generate_full_reroute()
    → PreferenceEngine.apply_preferences()
    → Rank strategies by overall_score
    → AIExplainer.explain_recovery() (for each strategy)
    → Store RecoveryStrategy records
    → Return ranked strategies

POST /api/v1/recovery/{id}/approve
    → Update strategy status → approved
    → AuditService.log()
    → NotificationService.notify()

POST /api/v1/recovery/{id}/execute
    → Process each RecoveryAction
    → Update JourneyNode statuses → recovered
    → Update Journey status → recovered
    → Recalculate resilience score
    → Update DigitalTwin
    → NotificationService.notify()
    → AuditService.log()
```

### 4. What-If Simulation Flow
```
POST /api/v1/journeys/{id}/simulate
    → Clone journey state (in memory)
    → Create virtual disruption
    → Run RippleImpactEngine on clone
    → Run RecoveryOptimizer on clone
    → Calculate resilience score before/after
    → Store Simulation record
    → Return simulation results (NO real data changed)

POST /api/v1/simulations/{id}/apply
    → Create real Disruption from simulation
    → Follow normal disruption flow
```

## Design Principles

1. **Separation of Concerns**: Engines contain only algorithms. Services handle orchestration. Routes handle HTTP.
2. **AI ≠ Everything**: LLMs handle natural language. Algorithms handle deterministic logic.
3. **Provider Abstraction**: All external services accessed through abstract interfaces.
4. **Audit Everything**: Every significant action creates an audit log entry.
5. **Fail Gracefully**: If autonomous recovery fails, escalate to human.
6. **Demo-First**: Application works fully with mock data, no external APIs needed.

## Security Architecture

```
Request → CORS Check → JWT Verification → Role Check → Rate Limit → Handler
                                                                       │
                                                                       ▼
                                                               Input Validation
                                                                       │
                                                                       ▼
                                                               Business Logic
                                                                       │
                                                                       ▼
                                                                 Audit Log
```

- **Authentication**: JWT tokens with configurable expiry
- **Authorization**: Role-based (traveler, ops_admin, sys_admin)
- **Passwords**: bcrypt hashed, never stored in plain text
- **Secrets**: Environment variables, never in source code
- **CORS**: Configurable allowed origins
- **Input**: Pydantic validation on all API inputs
