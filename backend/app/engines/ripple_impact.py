"""Ripple Impact Engine - Calculates cascading effects when a journey component is disrupted."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Configurable weights for impact scoring
DEFAULT_WEIGHTS = {
    "time": 0.25,
    "connection": 0.25,
    "financial": 0.20,
    "priority": 0.15,
    "criticality": 0.15,
}

IMPORTANCE_SCORES = {"critical": 1.0, "high": 0.75, "medium": 0.5, "low": 0.25}
FLEXIBILITY_SCORES = {"none": 0.0, "low": 0.25, "medium": 0.5, "high": 1.0}


@dataclass
class AffectedNodeInfo:
    node_id: str
    node_type: str
    provider: str
    impact_type: str  # direct or indirect
    reason: str
    severity_contribution: int
    cost_at_risk: float = 0.0
    time_shift_minutes: int = 0


@dataclass
class ImpactResult:
    impact_score: int  # 0-100
    severity_class: str  # low/moderate/high/severe/critical
    directly_affected: List[str]
    indirectly_affected: List[str]
    affected_details: List[AffectedNodeInfo] = field(default_factory=list)
    scoring_breakdown: Dict[str, float] = field(default_factory=dict)
    financial_exposure: float = 0.0
    currency: str = "INR"
    time_impact_minutes: int = 0
    total_nodes: int = 0
    critical_connections_at_risk: int = 0


class RippleImpactEngine:
    """Calculates the cascading impact of a disruption across a journey's dependency graph."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def calculate_impact(self, disruption, journey, nodes, dependencies) -> ImpactResult:
        """
        Main impact calculation.
        
        1. Build adjacency graph from dependencies
        2. BFS traverse from disrupted node
        3. Check time/location/connection conflicts
        4. Calculate weighted impact score
        5. Classify severity
        """
        logger.info(f"Calculating ripple impact for disruption {disruption.id} on journey {journey.id}")

        # Build lookups
        node_map = {n.id: n for n in nodes}
        disrupted_node = node_map.get(disruption.affected_node_id)
        if not disrupted_node:
            return ImpactResult(
                impact_score=0, severity_class="low",
                directly_affected=[], indirectly_affected=[],
                total_nodes=len(nodes)
            )

        # Build adjacency list (source -> [dependencies])
        adj: Dict[str, list] = {n.id: [] for n in nodes}
        dep_map: Dict[str, list] = {}
        for dep in dependencies:
            if dep.source_node_id in adj:
                adj[dep.source_node_id].append(dep)
            dep_map.setdefault(dep.source_node_id, []).append(dep)

        # Phase 1: BFS traversal from disrupted node
        directly_affected: List[AffectedNodeInfo] = []
        indirectly_affected: List[AffectedNodeInfo] = []
        visited = {disruption.affected_node_id}
        queue = deque()
        
        # Seed queue with direct downstream nodes
        for dep in adj.get(disruption.affected_node_id, []):
            if dep.target_node_id not in visited:
                queue.append((dep.target_node_id, dep, 1))  # (node_id, via_dependency, depth)
                visited.add(dep.target_node_id)

        delay_minutes = disruption.delay_minutes or 0
        critical_connections_at_risk = 0

        while queue:
            target_id, via_dep, depth = queue.popleft()
            target_node = node_map.get(target_id)
            if not target_node:
                continue

            # Check for time conflict
            has_time_conflict = self._check_time_conflict(
                disrupted_node, target_node, delay_minutes, via_dep
            )
            # Check for connection risk
            has_connection_risk = self._check_connection_risk(
                delay_minutes, via_dep
            )

            if via_dep and via_dep.is_critical and (has_time_conflict or has_connection_risk):
                critical_connections_at_risk += 1

            if has_time_conflict:
                reason = f"Time conflict: {delay_minutes}min delay exceeds {via_dep.buffer_minutes}min buffer"
                info = AffectedNodeInfo(
                    node_id=target_id,
                    node_type=target_node.type,
                    provider=target_node.provider or "",
                    impact_type="direct" if depth == 1 else "indirect",
                    reason=reason,
                    severity_contribution=self._node_severity(target_node),
                    cost_at_risk=target_node.cost or 0,
                    time_shift_minutes=delay_minutes - (via_dep.buffer_minutes if via_dep else 0)
                )
                if depth == 1:
                    directly_affected.append(info)
                else:
                    indirectly_affected.append(info)
            elif has_connection_risk:
                reason = f"Connection at risk: buffer {via_dep.buffer_minutes}min may be insufficient for {delay_minutes}min delay"
                info = AffectedNodeInfo(
                    node_id=target_id,
                    node_type=target_node.type,
                    provider=target_node.provider or "",
                    impact_type="indirect",
                    reason=reason,
                    severity_contribution=self._node_severity(target_node) // 2,
                    cost_at_risk=target_node.cost or 0 if has_time_conflict else 0,
                    time_shift_minutes=max(0, delay_minutes - (via_dep.buffer_minutes if via_dep else 0))
                )
                indirectly_affected.append(info)

            # Continue BFS downstream
            for dep in adj.get(target_id, []):
                if dep.target_node_id not in visited:
                    visited.add(dep.target_node_id)
                    queue.append((dep.target_node_id, dep, depth + 1))

        # Phase 2: Calculate component scores (each 0.0 to 1.0)
        all_affected = directly_affected + indirectly_affected
        total_journey_minutes = self._journey_duration_minutes(nodes)
        total_cost = sum((n.cost or 0) for n in nodes)
        total_critical_deps = sum(1 for d in dependencies if d.is_critical)
        total_connections = len(dependencies)

        # Time impact
        time_score = min(1.0, delay_minutes / max(total_journey_minutes, 1)) if delay_minutes > 0 else 0.0

        # Connection risk
        connection_score = (critical_connections_at_risk / max(total_connections, 1))

        # Financial exposure
        financial_exposure = sum(info.cost_at_risk for info in all_affected)
        financial_score = min(1.0, financial_exposure / max(total_cost, 1))

        # Traveler priority (importance-weighted)
        priority_scores = []
        for info in all_affected:
            node = node_map.get(info.node_id)
            if node:
                imp = IMPORTANCE_SCORES.get(node.importance or "medium", 0.5)
                priority_scores.append(imp)
        priority_score = sum(priority_scores) / max(len(priority_scores), 1) if priority_scores else 0.0

        # Dependency criticality
        criticality_score = critical_connections_at_risk / max(total_critical_deps, 1) if total_critical_deps > 0 else 0.0

        # Phase 3: Weighted sum
        raw_score = (
            self.weights["time"] * time_score +
            self.weights["connection"] * connection_score +
            self.weights["financial"] * financial_score +
            self.weights["priority"] * priority_score +
            self.weights["criticality"] * criticality_score
        )

        # Normalize to 0-100 (raw_score is 0-1 since weights sum to ~1)
        # Amplify to make scores more meaningful for demos
        impact_score = min(100, int(raw_score * 100 * 1.5 + len(all_affected) * 5))
        impact_score = max(0, min(100, impact_score))

        # Classify severity
        severity_class = self._classify_severity(impact_score)

        scoring_breakdown = {
            "time_impact": round(time_score, 3),
            "connection_risk": round(connection_score, 3),
            "financial_exposure": round(financial_score, 3),
            "traveler_priority": round(priority_score, 3),
            "dependency_criticality": round(criticality_score, 3),
            "w_time": self.weights["time"],
            "w_connection": self.weights["connection"],
            "w_financial": self.weights["financial"],
            "w_priority": self.weights["priority"],
            "w_criticality": self.weights["criticality"],
        }

        time_impact_minutes = delay_minutes

        logger.info(
            f"Impact calculated: score={impact_score}, severity={severity_class}, "
            f"directly_affected={len(directly_affected)}, indirectly_affected={len(indirectly_affected)}"
        )

        return ImpactResult(
            impact_score=impact_score,
            severity_class=severity_class,
            directly_affected=[info.node_id for info in directly_affected],
            indirectly_affected=[info.node_id for info in indirectly_affected],
            affected_details=directly_affected + indirectly_affected,
            scoring_breakdown=scoring_breakdown,
            financial_exposure=financial_exposure,
            currency="INR",
            time_impact_minutes=time_impact_minutes,
            total_nodes=len(nodes),
            critical_connections_at_risk=critical_connections_at_risk,
        )

    def _check_time_conflict(self, source_node, target_node, delay_minutes, dependency) -> bool:
        """Check if the delay makes the target node unreachable in time."""
        if not source_node.end_time or not target_node.start_time:
            return False
        buffer = dependency.buffer_minutes if dependency else 60
        delayed_arrival = source_node.end_time + timedelta(minutes=delay_minutes)
        return delayed_arrival > target_node.start_time

    def _check_connection_risk(self, delay_minutes, dependency) -> bool:
        """Check if the buffer is at risk but not necessarily a hard conflict."""
        if not dependency:
            return False
        buffer = dependency.buffer_minutes
        # At risk if delay is more than 50% of buffer
        return delay_minutes > buffer * 0.5

    def _node_severity(self, node) -> int:
        """Calculate a severity contribution for a node (0-25)."""
        importance = IMPORTANCE_SCORES.get(node.importance or "medium", 0.5)
        flexibility = FLEXIBILITY_SCORES.get(node.flexibility or "low", 0.25)
        return int((importance * (1 - flexibility)) * 25)

    def _journey_duration_minutes(self, nodes) -> int:
        """Calculate total journey duration in minutes."""
        if not nodes:
            return 0
        start_times = [n.start_time for n in nodes if n.start_time]
        end_times = [n.end_time for n in nodes if n.end_time]
        if not start_times or not end_times:
            return 0
        earliest = min(start_times)
        latest = max(end_times)
        return int((latest - earliest).total_seconds() / 60)

    def _classify_severity(self, score: int) -> str:
        """Classify impact score into severity level."""
        if score <= 20:
            return "low"
        elif score <= 40:
            return "moderate"
        elif score <= 60:
            return "high"
        elif score <= 80:
            return "severe"
        else:
            return "critical"
