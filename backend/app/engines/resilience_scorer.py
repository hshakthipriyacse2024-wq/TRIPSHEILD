"""Resilience Scorer - Calculates Journey Resilience Score (0-100)."""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

FLEXIBILITY_WEIGHTS = {"none": 0.0, "low": 0.25, "medium": 0.5, "high": 1.0}

class ResilienceScorer:
    """Calculates Journey Resilience Score (0-100) based on buffer, flexibility, exposure, and risk factors."""

    def calculate_score(self, journey, nodes, dependencies) -> Dict[str, Any]:
        if not nodes:
            return {
                "score": 100,
                "classification": "Highly resilient",
                "breakdown": {},
                "explanation": "Empty journey has no disruption vulnerability."
            }

        # 1. Connection buffer score (ideal buffer >= 60 mins)
        buffers = [d.buffer_minutes for d in dependencies if hasattr(d, 'buffer_minutes')]
        avg_buffer = (sum(buffers) / len(buffers)) if buffers else 90
        connection_buffer_score = min(1.0, avg_buffer / 90.0)

        # 2. Alternative availability & booking flexibility
        flexibilities = [FLEXIBILITY_WEIGHTS.get(getattr(n, 'flexibility', 'medium') or 'medium', 0.5) for n in nodes]
        booking_flexibility = sum(flexibilities) / len(flexibilities) if flexibilities else 0.5

        # 3. Dependency depth (longer chains = higher cascade vulnerability)
        dep_depth = len(dependencies) / max(len(nodes), 1)
        dependency_depth_score = max(0.0, 1.0 - (dep_depth * 0.3))

        # 4. Non-refundable exposure score
        total_cost = sum(getattr(n, 'cost', 0) or 0 for n in nodes)
        non_refundable_cost = sum(
            (getattr(n, 'cost', 0) or 0) for n in nodes 
            if getattr(n, 'flexibility', 'low') == 'none'
        )
        non_refundable_exposure = max(0.0, 1.0 - (non_refundable_cost / max(total_cost, 1)))

        # 5. Route risk (fewer transfers = higher resilience)
        flight_count = sum(1 for n in nodes if getattr(n, 'type', '') == 'flight')
        route_risk_score = max(0.2, 1.0 - (flight_count * 0.15))

        # Weighted final score calculation
        raw_score = (
            0.25 * connection_buffer_score +
            0.25 * booking_flexibility +
            0.20 * non_refundable_exposure +
            0.15 * dependency_depth_score +
            0.15 * route_risk_score
        )

        score = max(0, min(100, int(raw_score * 100)))

        # Classification
        if score >= 90:
            classification = "Highly resilient"
        elif score >= 75:
            classification = "Resilient"
        elif score >= 50:
            classification = "Moderate"
        elif score >= 25:
            classification = "Vulnerable"
        else:
            classification = "Critical"

        explanation = (
            f"Journey Resilience is rated {classification} ({score}/100). "
            f"Buffer adequacy is {int(connection_buffer_score * 100)}%, "
            f"booking flexibility is {int(booking_flexibility * 100)}%, and "
            f"financial exposure protection is {int(non_refundable_exposure * 100)}%."
        )

        return {
            "score": score,
            "classification": classification,
            "explanation": explanation,
            "breakdown": {
                "connection_buffer_score": round(connection_buffer_score, 2),
                "alternative_availability": round(booking_flexibility, 2),
                "booking_flexibility": round(booking_flexibility, 2),
                "dependency_depth": round(dependency_depth_score, 2),
                "non_refundable_exposure": round(non_refundable_exposure, 2),
                "route_risk": round(route_risk_score, 2)
            }
        }
