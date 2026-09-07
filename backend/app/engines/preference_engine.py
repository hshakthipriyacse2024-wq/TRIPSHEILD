from typing import Dict, List, Any

class PreferenceEngine:
    def normalize_weights(self, preferences) -> Dict[str, float]:
        if not preferences:
            return {"budget": 0.25, "speed": 0.25, "comfort": 0.25, "minimal_changes": 0.25}
        total = (preferences.budget_priority + preferences.speed_priority + 
                 preferences.comfort_priority + preferences.minimal_changes_priority)
        if total == 0: total = 1
        return {
            "budget": preferences.budget_priority / total,
            "speed": preferences.speed_priority / total,
            "comfort": preferences.comfort_priority / total,
            "minimal_changes": preferences.minimal_changes_priority / total
        }

    def apply_preferences(self, strategies: List[Dict[str, Any]], preferences) -> List[Dict[str, Any]]:
        weights = self.normalize_weights(preferences)
        for s in strategies:
            # Re-score based on weights
            s["overall_score"] = (weights["time_saved"] * s["time_saved_minutes"] + 
                                  weights["budget"] * (1 - s["additional_cost"]/10000)) * 100 # simplified
        strategies.sort(key=lambda x: x["overall_score"], reverse=True)
        return strategies
