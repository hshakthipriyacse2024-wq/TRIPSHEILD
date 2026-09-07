# TripShield AI — Journey Digital Twin

## Concept

The Journey Digital Twin is a live, graph-based representation of a travel itinerary. Unlike traditional flat itinerary lists, the Digital Twin models the **dependency network** between travel components, enabling cascading impact analysis and intelligent recovery.

## Graph Model

```
A journey is a directed acyclic graph (DAG) where:
- Nodes = Travel components (flights, hotels, activities, etc.)
- Edges = Dependencies (connects_to, depends_on, precedes, etc.)
```

### Example: Chennai → Delhi → Paris

```
[Flight: MAA→DEL]
       │ connects_to (buffer: 30min, critical)
       ▼
[Airport Transfer: DEL Airport → Hotel]
       │ depends_on (buffer: 15min)
       ▼
[Hotel: The Imperial Delhi] ──precedes──▶ [Activity: Red Fort Tour]
       │ depends_on (buffer: 60min, critical)     │ precedes (buffer: 150min)
       ▼                                           ▼
[Flight: DEL→CDG]                          [Restaurant: Bukhara]
       │ connects_to (buffer: 30min, critical)
       ▼
[Airport Transfer: CDG → Hotel]
       │ depends_on (buffer: 30min)
       ▼
[Hotel: Le Marais Paris] ──precedes──▶ [Activity: Eiffel Tower]
                                              │ precedes (buffer: 120min)
                                              ▼
                                       [Restaurant: Le Comptoir]
```

## Node Properties

Each node carries:

| Property | Type | Purpose |
|----------|------|---------|
| `id` | UUID | Unique identifier |
| `type` | enum | flight, hotel, activity, etc. |
| `provider` | string | Service provider name |
| `location` | string | Geographic location |
| `lat/lng` | float | Coordinates for mapping |
| `start_time` | datetime | When the service begins |
| `end_time` | datetime | When the service ends |
| `status` | enum | confirmed, at_risk, affected, recovered, cancelled |
| `cost` | decimal | Booking cost |
| `booking_reference` | string | Provider booking ID |
| `flexibility` | enum | none, low, medium, high |
| `importance` | enum | critical, high, medium, low |
| `cancellation_policy` | JSON | Refund rules |
| `details` | JSON | Type-specific details |

## Edge Properties

Each dependency edge carries:

| Property | Type | Purpose |
|----------|------|---------|
| `relationship_type` | enum | Type of dependency |
| `buffer_minutes` | int | Time buffer between connected nodes |
| `is_critical` | bool | Whether this is a critical connection |

## Status Visualization

```
🟢 Confirmed — Service is booked and on schedule
🟡 At Risk   — Service may be affected by upstream disruption
🔴 Affected  — Service is impacted and needs recovery
🔵 Recovered — Service was affected but has been recovered
⚫ Cancelled — Service has been cancelled
```

## Frontend Visualization

The Digital Twin is rendered using **React Flow** with:

1. **Custom node components** showing type icon, name, time, status with color coding
2. **Animated edges** for critical dependencies
3. **Interactive features**: zoom, pan, click-to-inspect
4. **Real-time updates** when disruptions occur (nodes change color)
5. **Layout algorithm** positioning nodes in a top-to-bottom flow

## Use Cases

### 1. Journey Understanding
The traveler sees their entire trip as an interconnected system, not a flat list.

### 2. Disruption Visualization
When a disruption occurs, affected nodes visually change color, showing the cascade.

### 3. Recovery Planning
Recovery strategies reference specific nodes and dependencies, visible in the twin.

### 4. What-If Analysis
Simulations show hypothetical status changes without modifying the real twin.

### 5. Resilience Assessment
The graph structure determines connection vulnerabilities and buffer adequacy.
