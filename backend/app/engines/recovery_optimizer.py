"""Recovery Optimization Engine - Generates, scores, and ranks recovery strategies."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import timedelta
import logging
import random

logger = logging.getLogger(__name__)


@dataclass
class RecoveryActionData:
    action_type: str  # rebook/reschedule/cancel/add/modify/keep
    description: str
    original_node_id: Optional[str] = None
    replacement_node_id: Optional[str] = None
    old_details: Dict[str, Any] = field(default_factory=dict)
    new_details: Dict[str, Any] = field(default_factory=dict)
    cost_difference: float = 0.0


@dataclass
class RecoveryStrategyData:
    title: str
    description: str
    changed_components: List[str] = field(default_factory=list)
    preserved_components: List[str] = field(default_factory=list)
    additional_cost: float = 0.0
    currency: str = "INR"
    time_saved_minutes: int = 0
    num_changes: int = 0
    feasibility_score: float = 0.0
    comfort_score: float = 0.0
    urgency_score: float = 0.0
    financial_impact_score: float = 0.0
    recovery_confidence: float = 0.0
    overall_score: float = 0.0
    explanation: str = ""
    is_recommended: bool = False
    rank: int = 0
    actions: List[RecoveryActionData] = field(default_factory=list)


# Alternative flight options for demo
ALTERNATIVE_FLIGHTS = [
    {"airline": "IndiGo", "flight": "6E-204", "departure": "10:30", "arrival": "13:00", "cost": 4800},
    {"airline": "SpiceJet", "flight": "SG-152", "departure": "11:00", "arrival": "13:30", "cost": 4200},
    {"airline": "Vistara", "flight": "UK-826", "departure": "12:00", "arrival": "14:15", "cost": 6500},
    {"airline": "Air India", "flight": "AI-544", "departure": "14:00", "arrival": "16:30", "cost": 5200},
    {"airline": "IndiGo", "flight": "6E-318", "departure": "16:30", "arrival": "19:00", "cost": 3900},
]

ALTERNATIVE_TRAINS = [
    {"operator": "Rajdhani Express", "train": "12952", "departure": "16:00", "arrival": "04:00+1", "cost": 2800},
    {"operator": "Shatabdi Express", "train": "12004", "departure": "06:00", "arrival": "14:00", "cost": 1800},
]


class RecoveryOptimizer:
    """Generates multiple recovery strategies and scores them against traveler preferences."""

    def generate_strategies(
        self, disruption, impact, journey, nodes, dependencies, preferences, providers
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple recovery strategies for a disruption.
        
        Strategy types:
        1. Minimal Recovery - change only disrupted node
        2. Connection Preserving - change disrupted + adjust connections  
        3. Cost Optimized - cheapest recovery path
        4. Comfort Optimized - least traveler inconvenience
        5. Full Reroute - change everything from disruption forward
        """
        logger.info(f"Generating recovery strategies for disruption {disruption.id}")

        node_map = {n.id: n for n in nodes}
        disrupted_node = node_map.get(disruption.affected_node_id)
        if not disrupted_node:
            return []

        # Get affected node IDs from impact analysis
        affected_ids = set()
        if impact:
            affected_ids = set(
                (impact.directly_affected if hasattr(impact, 'directly_affected') else []) +
                (impact.indirectly_affected if hasattr(impact, 'indirectly_affected') else [])
            )

        all_node_ids = [n.id for n in nodes]
        delay_minutes = disruption.delay_minutes or 0
        original_cost = disrupted_node.cost or 0

        strategies = []

        # Strategy 1: Minimal Recovery (rebook only the disrupted component)
        alt = ALTERNATIVE_FLIGHTS[0] if disrupted_node.type == "flight" else ALTERNATIVE_FLIGHTS[1]
        cost_diff = alt["cost"] - original_cost
        time_improvement = max(0, delay_minutes - 120)  # Assumes alt flight is ~2h later than original
        strategies.append(RecoveryStrategyData(
            title=f"Rebook to {alt['airline']} {alt['flight']}",
            description=f"Change to {alt['airline']} flight {alt['flight']} departing at {alt['departure']}. "
                        f"All downstream bookings remain unchanged.",
            changed_components=[disruption.affected_node_id],
            preserved_components=[nid for nid in all_node_ids if nid != disruption.affected_node_id],
            additional_cost=cost_diff,
            currency=disrupted_node.currency or "INR",
            time_saved_minutes=time_improvement,
            num_changes=1,
            feasibility_score=0.92,
            comfort_score=0.75,
            urgency_score=0.85,
            financial_impact_score=max(0.0, 1.0 - abs(cost_diff) / max(original_cost, 1)),
            recovery_confidence=0.88,
            actions=[RecoveryActionData(
                action_type="rebook",
                description=f"Rebook to {alt['airline']} {alt['flight']} at {alt['departure']}",
                original_node_id=disruption.affected_node_id,
                old_details={"provider": disrupted_node.provider, "cost": original_cost},
                new_details={"provider": alt["airline"], "flight": alt["flight"],
                             "departure": alt["departure"], "arrival": alt["arrival"],
                             "cost": alt["cost"]},
                cost_difference=cost_diff,
            )]
        ))

        # Strategy 2: Connection Preserving (change flight + adjust downstream timing)
        alt2 = ALTERNATIVE_FLIGHTS[1]
        cost_diff2 = alt2["cost"] - original_cost
        changed_ids = [disruption.affected_node_id]
        # Add directly connected nodes that need rescheduling
        for dep in dependencies:
            if dep.source_node_id == disruption.affected_node_id:
                changed_ids.append(dep.target_node_id)
        preserved_ids = [nid for nid in all_node_ids if nid not in changed_ids]

        actions2 = [
            RecoveryActionData(
                action_type="rebook",
                description=f"Rebook to {alt2['airline']} {alt2['flight']} at {alt2['departure']}",
                original_node_id=disruption.affected_node_id,
                old_details={"provider": disrupted_node.provider, "cost": original_cost},
                new_details={"provider": alt2["airline"], "flight": alt2["flight"],
                             "departure": alt2["departure"], "cost": alt2["cost"]},
                cost_difference=cost_diff2,
            ),
        ]
        # Add reschedule actions for downstream nodes
        for nid in changed_ids[1:]:
            node = node_map.get(nid)
            if node:
                actions2.append(RecoveryActionData(
                    action_type="reschedule",
                    description=f"Reschedule {node.type}: {node.provider or 'service'} to align with new arrival",
                    original_node_id=nid,
                    old_details={"start_time": str(node.start_time)},
                    new_details={"start_time": "adjusted"},
                    cost_difference=0,
                ))

        strategies.append(RecoveryStrategyData(
            title=f"Rebook Flight + Adjust Connections",
            description=f"Switch to {alt2['airline']} {alt2['flight']} and reschedule {len(changed_ids)-1} "
                        f"downstream booking(s) to preserve all connections.",
            changed_components=changed_ids,
            preserved_components=preserved_ids,
            additional_cost=cost_diff2,
            currency=disrupted_node.currency or "INR",
            time_saved_minutes=max(0, delay_minutes - 90),
            num_changes=len(changed_ids),
            feasibility_score=0.85,
            comfort_score=0.80,
            urgency_score=0.80,
            financial_impact_score=max(0.0, 1.0 - abs(cost_diff2) / max(original_cost, 1)),
            recovery_confidence=0.82,
            actions=actions2,
        ))

        # Strategy 3: Cost Optimized (cheapest option)
        cheapest = min(ALTERNATIVE_FLIGHTS, key=lambda x: x["cost"])
        cost_diff3 = cheapest["cost"] - original_cost
        strategies.append(RecoveryStrategyData(
            title=f"Budget Recovery: {cheapest['airline']} {cheapest['flight']}",
            description=f"Most affordable option: {cheapest['airline']} {cheapest['flight']} "
                        f"at {cheapest['departure']}. Saves ₹{abs(cost_diff3) if cost_diff3 < 0 else 0}.",
            changed_components=[disruption.affected_node_id],
            preserved_components=[nid for nid in all_node_ids if nid != disruption.affected_node_id],
            additional_cost=cost_diff3,
            currency=disrupted_node.currency or "INR",
            time_saved_minutes=max(0, delay_minutes - 180),
            num_changes=1,
            feasibility_score=0.88,
            comfort_score=0.55,
            urgency_score=0.60,
            financial_impact_score=0.95,
            recovery_confidence=0.80,
            actions=[RecoveryActionData(
                action_type="rebook",
                description=f"Rebook to {cheapest['airline']} {cheapest['flight']}",
                original_node_id=disruption.affected_node_id,
                old_details={"provider": disrupted_node.provider, "cost": original_cost},
                new_details={"provider": cheapest["airline"], "flight": cheapest["flight"],
                             "departure": cheapest["departure"], "cost": cheapest["cost"]},
                cost_difference=cost_diff3,
            )]
        ))

        # Strategy 4: Comfort Optimized (premium option, early arrival)
        premium = ALTERNATIVE_FLIGHTS[2]  # Vistara
        cost_diff4 = premium["cost"] - original_cost
        strategies.append(RecoveryStrategyData(
            title=f"Premium Recovery: {premium['airline']} {premium['flight']}",
            description=f"Premium option with {premium['airline']}: better service, "
                        f"arrives at {premium['arrival']}. Higher cost but maximum comfort.",
            changed_components=[disruption.affected_node_id],
            preserved_components=[nid for nid in all_node_ids if nid != disruption.affected_node_id],
            additional_cost=cost_diff4,
            currency=disrupted_node.currency or "INR",
            time_saved_minutes=max(0, delay_minutes - 150),
            num_changes=1,
            feasibility_score=0.90,
            comfort_score=0.95,
            urgency_score=0.75,
            financial_impact_score=max(0.0, 1.0 - abs(cost_diff4) / max(original_cost, 1)),
            recovery_confidence=0.90,
            actions=[RecoveryActionData(
                action_type="rebook",
                description=f"Rebook to {premium['airline']} {premium['flight']}",
                original_node_id=disruption.affected_node_id,
                old_details={"provider": disrupted_node.provider, "cost": original_cost},
                new_details={"provider": premium["airline"], "flight": premium["flight"],
                             "departure": premium["departure"], "cost": premium["cost"]},
                cost_difference=cost_diff4,
            )]
        ))

        # Strategy 5: Alternative Transport (train if available, for domestic)
        if disrupted_node.type == "flight":
            train = ALTERNATIVE_TRAINS[0]
            cost_diff5 = train["cost"] - original_cost
            strategies.append(RecoveryStrategyData(
                title=f"Alternative Transport: {train['operator']}",
                description=f"Switch to train ({train['operator']} {train['train']}). "
                            f"Longer travel time but significantly cheaper and avoids airport delays.",
                changed_components=[disruption.affected_node_id],
                preserved_components=[nid for nid in all_node_ids if nid != disruption.affected_node_id],
                additional_cost=cost_diff5,
                currency=disrupted_node.currency or "INR",
                time_saved_minutes=-300,  # trains take longer
                num_changes=1,
                feasibility_score=0.75,
                comfort_score=0.65,
                urgency_score=0.40,
                financial_impact_score=0.98,
                recovery_confidence=0.95,
                actions=[RecoveryActionData(
                    action_type="rebook",
                    description=f"Switch to {train['operator']} train {train['train']}",
                    original_node_id=disruption.affected_node_id,
                    old_details={"provider": disrupted_node.provider, "type": "flight", "cost": original_cost},
                    new_details={"provider": train["operator"], "type": "train",
                                 "train": train["train"], "departure": train["departure"],
                                 "cost": train["cost"]},
                    cost_difference=cost_diff5,
                )]
            ))

        # Score all strategies against preferences
        strategies = self._score_strategies(strategies, preferences)

        # Sort by overall_score descending, assign ranks
        strategies.sort(key=lambda s: s.overall_score, reverse=True)
        for i, s in enumerate(strategies):
            s.rank = i + 1
            s.is_recommended = (i == 0)

        # Generate explanations from actual calculated values
        for s in strategies:
            s.explanation = self._generate_explanation(s, strategies[0] if strategies else s)

        # Convert to dicts for API response
        return [self._to_dict(s) for s in strategies]

    def _score_strategies(
        self, strategies: List[RecoveryStrategyData], preferences
    ) -> List[RecoveryStrategyData]:
        """Score each strategy based on traveler preference weights."""
        # Default preference weights if none provided
        pref_speed = getattr(preferences, 'speed_priority', 70) if preferences else 70
        pref_budget = getattr(preferences, 'budget_priority', 50) if preferences else 50
        pref_comfort = getattr(preferences, 'comfort_priority', 60) if preferences else 60
        pref_minimal = getattr(preferences, 'minimal_changes_priority', 50) if preferences else 50
        
        # Normalize weights
        raw = {
            "time": pref_speed,
            "cost": pref_budget,
            "comfort": pref_comfort,
            "feasibility": 70,  # system baseline
            "preservation": pref_minimal,
            "urgency": 60,  # system baseline
        }
        total = sum(raw.values())
        weights = {k: v / total for k, v in raw.items()}

        for s in strategies:
            # Normalize time score (more time saved = better)
            time_score = min(1.0, max(0.0, (s.time_saved_minutes + 300) / 600))
            # Cost score (lower additional cost = better)
            cost_score = max(0.0, 1.0 - max(0, s.additional_cost) / 10000)
            # Preservation score
            total_components = len(s.changed_components) + len(s.preserved_components)
            preservation_score = len(s.preserved_components) / max(total_components, 1)

            s.overall_score = round((
                weights["time"] * time_score +
                weights["cost"] * cost_score +
                weights["comfort"] * s.comfort_score +
                weights["feasibility"] * s.feasibility_score +
                weights["preservation"] * preservation_score +
                weights["urgency"] * s.urgency_score
            ) * 100, 1)

        return strategies

    def _generate_explanation(self, strategy: RecoveryStrategyData, best: RecoveryStrategyData) -> str:
        """Generate a human-readable explanation from actual calculated values."""
        parts = []

        if len(strategy.preserved_components) > 0:
            parts.append(f"preserves {len(strategy.preserved_components)} of your bookings")

        if strategy.time_saved_minutes > 0:
            hours = strategy.time_saved_minutes // 60
            mins = strategy.time_saved_minutes % 60
            if hours > 0:
                parts.append(f"recovers {hours}h {mins}m of travel time")
            else:
                parts.append(f"recovers {mins} minutes of travel time")
        elif strategy.time_saved_minutes < 0:
            parts.append(f"adds {abs(strategy.time_saved_minutes)} minutes to travel time")

        if strategy.additional_cost < 0:
            parts.append(f"saves ₹{abs(int(strategy.additional_cost))}")
        elif strategy.additional_cost > 0:
            parts.append(f"costs ₹{int(strategy.additional_cost)} more")
        else:
            parts.append("has no additional cost")

        if strategy.num_changes == 1:
            parts.append("requires only 1 itinerary change")
        else:
            parts.append(f"requires {strategy.num_changes} itinerary changes")

        confidence_pct = int(strategy.recovery_confidence * 100)
        parts.append(f"has {confidence_pct}% recovery confidence")

        explanation = f"This option {', '.join(parts)}."

        if strategy.is_recommended:
            explanation = f"RECOMMENDED: {explanation} This is the best overall option based on your preferences."

        return explanation

    def _to_dict(self, strategy: RecoveryStrategyData) -> Dict[str, Any]:
        """Convert strategy dataclass to dict for API response."""
        return {
            "title": strategy.title,
            "description": strategy.description,
            "changed_components": strategy.changed_components,
            "preserved_components": strategy.preserved_components,
            "additional_cost": strategy.additional_cost,
            "currency": strategy.currency,
            "time_saved_minutes": strategy.time_saved_minutes,
            "num_changes": strategy.num_changes,
            "feasibility_score": round(strategy.feasibility_score, 2),
            "comfort_score": round(strategy.comfort_score, 2),
            "urgency_score": round(strategy.urgency_score, 2),
            "financial_impact_score": round(strategy.financial_impact_score, 2),
            "recovery_confidence": round(strategy.recovery_confidence, 2),
            "overall_score": round(strategy.overall_score, 1),
            "explanation": strategy.explanation,
            "is_recommended": strategy.is_recommended,
            "rank": strategy.rank,
            "actions": [
                {
                    "action_type": a.action_type,
                    "description": a.description,
                    "original_node_id": a.original_node_id,
                    "replacement_node_id": a.replacement_node_id,
                    "old_details": a.old_details,
                    "new_details": a.new_details,
                    "cost_difference": a.cost_difference,
                }
                for a in strategy.actions
            ],
        }
