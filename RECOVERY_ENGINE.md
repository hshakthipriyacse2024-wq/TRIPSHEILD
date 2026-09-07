# TripShield AI — Recovery Engine Documentation

## Overview

The Recovery Optimization Engine is the heart of TripShield AI. When a disruption occurs, it generates multiple recovery strategies, scores them against traveler preferences, and provides explainable recommendations.

## Recovery Pipeline

```
Disruption Detected
       ↓
Impact Analysis (from Ripple Impact Engine)
       ↓
Load Affected Nodes & Dependencies
       ↓
Query Mock Providers for Alternatives
       ↓
┌──────────────────────────────────────┐
│     Strategy Generators              │
│  ┌──────────────────────────────┐   │
│  │ Minimal Recovery             │   │
│  │ (Change only disrupted node) │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Connection Preserving        │   │
│  │ (Preserve downstream links)  │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Cost Optimized               │   │
│  │ (Minimize additional cost)   │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Comfort Optimized            │   │
│  │ (Minimize traveler impact)   │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Full Reroute                 │   │
│  │ (Change from disruption fwd) │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
       ↓
Preference-Weighted Scoring
       ↓
Rank & Recommend
       ↓
Generate Explanations
```

## Scoring Function

```
Recovery Score = Σ(wᵢ × Scoreᵢ) × 100

Where:
  Score_time       = normalized time improvement (0-1)
  Score_cost       = normalized cost efficiency (0-1)
  Score_comfort    = comfort rating (0-1)
  Score_feasibility = likelihood of success (0-1)
  Score_preservation = ratio of preserved bookings (0-1)
  Score_urgency    = time-sensitivity rating (0-1)
```

## Weight Derivation from Preferences

```python
raw_weights = {
    'time': preferences.speed_priority,          # 0-100
    'cost': preferences.budget_priority,          # 0-100
    'comfort': preferences.comfort_priority,      # 0-100
    'feasibility': 70,                            # system baseline
    'preservation': preferences.minimal_changes,  # 0-100
    'urgency': 60                                 # system baseline
}

# Normalize to sum = 1.0
total = sum(raw_weights.values())
weights = {k: v / total for k, v in raw_weights.items()}
```

## Strategy Generation Details

### Minimal Recovery
- Changes only the disrupted component
- Queries provider for next available alternative
- Lowest number of changes (1)
- May not resolve all downstream conflicts

### Connection Preserving
- Changes disrupted + immediate connections
- Ensures all critical connections are maintained
- Recalculates buffer times
- Preferred when journey has tight connections

### Cost Optimized
- Searches all alternatives across providers
- Selects combination with lowest additional cost
- May sacrifice time or comfort for savings
- Considers cancellation fees and refund policies

### Comfort Optimized
- Minimizes traveler inconvenience
- Preserves important activities and dining
- Avoids red-eye flights and long layovers
- Considers accessibility requirements

### Full Reroute
- Replaces all nodes from disruption point forward
- Most comprehensive but most disruptive
- Used for severe disruptions (cancellations, closures)
- Highest number of changes but potentially best outcome

## Explanation Generation

Explanations are generated from actual calculated values, NEVER fabricated:

```python
explanation = f"Option {rank} was selected because it "
parts = []

if strategy.preserved_count > 0:
    parts.append(f"preserves {strategy.preserved_count} of your bookings")
if strategy.time_saved > 0:
    parts.append(f"saves {strategy.time_saved} minutes")
if strategy.additional_cost < 0:
    parts.append(f"saves ₹{abs(strategy.additional_cost)}")
elif strategy.additional_cost > 0:
    parts.append(f"costs ₹{strategy.additional_cost} more")
if strategy.num_changes == 1:
    parts.append("requires only 1 change")

explanation += ", ".join(parts) + "."
```

## Human-in-the-Loop Modes

| Mode | Behavior |
|------|----------|
| **Recommend Only** | Generate and display options. No execution. |
| **Ask for Approval** | Generate options, recommend best, wait for user approval. **(Default)** |
| **Autonomous Recovery** | Automatically execute the highest-scored strategy if confidence > 0.8. |

## Recovery Execution

When a strategy is approved and executed:

1. Each `RecoveryAction` is processed:
   - `rebook`: Replace node with alternative
   - `reschedule`: Update times on existing node
   - `cancel`: Mark node as cancelled
   - `modify`: Update node details
   - `keep`: No change needed
2. Affected `JourneyNode` statuses update to `recovered`
3. `Journey` status updates to `recovered`
4. Resilience score is recalculated
5. Notifications are sent
6. Audit log entry is created with full decision trail

## Failure Handling

If recovery execution fails at any step:
1. Strategy status → `failed`
2. Already-executed actions are NOT rolled back (they represent real-world bookings)
3. Notification: "Recovery partially failed. Human assistance required."
4. Journey status → `recovering` (not resolved)
5. Audit log captures the failure point and reason
