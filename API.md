# TripShield AI — API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints except `/auth/register`, `/auth/login`, and `/health` require a JWT bearer token.

```
Authorization: Bearer <token>
```

---

## Auth Endpoints

### POST /auth/register
Create a new user account.

**Request Body:**
```json
{
  "email": "traveler@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "phone": "+91-9876543210"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### POST /auth/login
Authenticate and get a JWT token.

**Request Body:**
```json
{
  "email": "traveler@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### GET /auth/me
Get current authenticated user profile.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "traveler@example.com",
  "full_name": "John Doe",
  "phone": "+91-9876543210",
  "role": "traveler",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Journey Endpoints

### POST /journeys
Create a new journey.

**Request Body:**
```json
{
  "title": "Chennai to Paris Adventure",
  "description": "Business trip with sightseeing",
  "origin": "Chennai",
  "destination": "Paris",
  "start_date": "2024-03-15T06:00:00Z",
  "end_date": "2024-03-20T22:00:00Z"
}
```

### GET /journeys
List all journeys for the current user.

### GET /journeys/{id}
Get journey details including nodes and dependencies.

### PUT /journeys/{id}
Update journey metadata.

### DELETE /journeys/{id}
Delete a journey and all associated data.

---

## Node Endpoints

### POST /journeys/{id}/nodes
Add a travel component to a journey.

**Request Body:**
```json
{
  "type": "flight",
  "provider": "Air India",
  "location": "Chennai (MAA)",
  "latitude": 12.9941,
  "longitude": 80.1709,
  "destination_location": "Delhi (DEL)",
  "dest_latitude": 28.5562,
  "dest_longitude": 77.1000,
  "start_time": "2024-03-15T06:00:00Z",
  "end_time": "2024-03-15T08:30:00Z",
  "cost": 5500,
  "currency": "INR",
  "booking_reference": "AI-542-DEMO",
  "flexibility": "low",
  "importance": "critical",
  "details": {
    "flight_number": "AI-542",
    "airline": "Air India",
    "departure_terminal": "T1",
    "arrival_terminal": "T3"
  },
  "sequence_order": 1
}
```

### PUT /journeys/{id}/nodes/{nodeId}
Update a node.

### DELETE /journeys/{id}/nodes/{nodeId}
Remove a node.

---

## Dependency Endpoints

### POST /journeys/{id}/dependencies
Create a dependency between two nodes.

**Request Body:**
```json
{
  "source_node_id": "uuid-of-flight",
  "target_node_id": "uuid-of-transfer",
  "relationship_type": "connects_to",
  "buffer_minutes": 30,
  "is_critical": true
}
```

### DELETE /journeys/{id}/dependencies/{depId}
Remove a dependency.

---

## Digital Twin & Resilience

### GET /journeys/{id}/digital-twin
Get complete graph data for visualization.

**Response (200):**
```json
{
  "journey": { "id": "...", "title": "...", "status": "active" },
  "nodes": [ { "id": "...", "type": "flight", "status": "confirmed", ... } ],
  "dependencies": [ { "source_node_id": "...", "target_node_id": "...", ... } ],
  "resilience_score": 78
}
```

### GET /journeys/{id}/resilience-score
Calculate and return the journey resilience score.

**Response (200):**
```json
{
  "score": 78,
  "classification": "Resilient",
  "breakdown": {
    "connection_buffer": 0.85,
    "alternative_availability": 0.70,
    "booking_flexibility": 0.60,
    "dependency_depth": 0.90,
    "non_refundable_exposure": 0.75,
    "route_risk": 0.80
  },
  "explanation": "Your journey is rated Resilient (78/100). Strong connection buffers and moderate flexibility provide good protection."
}
```

---

## Disruption Endpoints

### POST /disruptions
Create/report a disruption.

**Request Body:**
```json
{
  "journey_id": "uuid",
  "affected_node_id": "uuid",
  "type": "flight_delay",
  "description": "Flight AI-542 delayed by 4 hours due to technical issues",
  "delay_minutes": 240,
  "is_simulated": true
}
```

**Response (201):** Disruption with automatic impact analysis.

### GET /disruptions
List disruptions, optionally filtered by journey_id.

### GET /disruptions/{id}
Get disruption details with impact analysis.

---

## Recovery Endpoints

### POST /journeys/{id}/recovery-options
Generate recovery strategies for the latest disruption.

**Response (200):**
```json
{
  "disruption_id": "uuid",
  "strategies": [
    {
      "id": "uuid",
      "title": "Rebook to Later Flight",
      "description": "Change to IndiGo 6E-204 departing at 10:30",
      "additional_cost": 800,
      "time_saved_minutes": 120,
      "num_changes": 1,
      "overall_score": 87.5,
      "is_recommended": true,
      "explanation": "This option preserves your hotel and activity bookings..."
    },
    ...
  ]
}
```

### POST /recovery/{strategyId}/approve
Approve a recovery strategy.

### POST /recovery/{strategyId}/execute
Execute an approved recovery (updates journey).

### POST /recovery/{strategyId}/reject
Reject a recovery strategy.

---

## Simulator Endpoints

### POST /journeys/{id}/simulate
Run a what-if simulation without modifying real data.

**Request Body:**
```json
{
  "disruption_type": "flight_delay",
  "parameters": {
    "delay_minutes": 240
  }
}
```

**Response (200):**
```json
{
  "simulation_id": "uuid",
  "impact": { "impact_score": 72, "severity_class": "severe", ... },
  "recovery_options": [ ... ],
  "resilience_score_before": 78,
  "resilience_score_after": 45
}
```

### POST /simulations/{id}/apply
Apply a simulation result to the real journey.

### POST /simulations/{id}/discard
Discard a simulation.

---

## Guardian Endpoint

### POST /guardian/chat
Chat with TripShield Guardian AI.

**Request Body:**
```json
{
  "message": "What happens if my flight is delayed by 3 hours?",
  "journey_id": "uuid"
}
```

**Response (200):**
```json
{
  "response": "If your flight AI-542 from Chennai to Delhi is delayed by 3 hours, it would affect 4 downstream bookings...",
  "context": {
    "journey_used": true,
    "nodes_referenced": 4
  }
}
```

---

## Demo Endpoints

### POST /demo/load
Load the demo journey (Chennai → Delhi → Paris).

### POST /demo/simulate-delay
Simulate a 4-hour delay on the first flight.

### POST /demo/simulate-cancellation
Simulate a flight cancellation.

---

## Analytics Endpoints

### GET /analytics/dashboard
Dashboard statistics.

### GET /analytics/recovery
Recovery performance metrics.

---

## Admin Endpoints (ops_admin, sys_admin)

### GET /admin/users
List all users.

### PUT /admin/users/{id}/role
Change a user's role.

### GET /admin/audit-logs
View audit log entries.

### GET /admin/system-health
System health status.

---

## Notifications

### GET /notifications
List user notifications.

### PUT /notifications/{id}/read
Mark a notification as read.

---

## Preferences

### GET /preferences
Get current user's travel preferences.

### PUT /preferences
Update travel preferences.

---

## Health

### GET /health
Public health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error description"
}
```

| Code | Meaning |
|------|---------|
| 400 | Bad Request — validation error |
| 401 | Unauthorized — missing/invalid token |
| 403 | Forbidden — insufficient role |
| 404 | Not Found |
| 409 | Conflict — duplicate resource |
| 422 | Unprocessable Entity — validation error |
| 500 | Internal Server Error |
