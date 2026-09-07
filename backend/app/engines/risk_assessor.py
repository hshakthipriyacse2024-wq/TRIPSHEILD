from typing import Dict, Any, List

class RiskAssessor:
    def assess_journey(self, journey, nodes, dependencies) -> List[Dict[str, Any]]:
        risks = []
        for n in nodes:
            risks.append(self.assess_node(n, dependencies))
        return risks
        
    def assess_node(self, node, dependencies) -> Dict[str, Any]:
        overall = 0.3
        return {
            "node_id": node.id,
            "weather_risk": 0.2,
            "delay_history_risk": 0.3,
            "congestion_risk": 0.4,
            "connection_buffer_risk": 0.1,
            "route_risk": 0.2,
            "provider_reliability": 0.9,
            "overall_risk": overall,
            "risk_level": "medium" if overall > 0.25 else "low",
            "explanation": "Normal conditions."
        }
