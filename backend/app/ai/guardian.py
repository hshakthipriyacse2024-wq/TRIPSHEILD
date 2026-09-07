"""TripShield Guardian AI - Context-aware conversational assistant for travel resilience."""
from app.ai.base import LLMProvider
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MockLLMProvider(LLMProvider):
    """Template-based LLM provider that generates grounded, data-backed responses for human questions."""

    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        return "Based on your Journey Digital Twin analysis, your itinerary is protected by active contingency rules."

    def explain_recovery(self, strategy: Dict[str, Any], impact: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        title = strategy.get("title", "Recommended Option")
        score = strategy.get("overall_score", 85)
        cost = strategy.get("additional_cost", 0)
        cost_text = f"saves ₹{abs(cost)}" if cost < 0 else f"costs ₹{cost} extra" if cost > 0 else "costs ₹0 extra"
        return f"I recommend '{title}' (Score: {score}/100) because it preserves downstream hotel & activity bookings and {cost_text}."

    def chat(self, message: str, context: Dict[str, Any]) -> str:
        msg_lower = message.lower()
        j_info = context.get("journey", {})
        nodes = j_info.get("nodes", [])
        disruptions = context.get("disruptions", [])
        recoveries = context.get("recoveries", [])

        journey_dict = j_info.get("journey", {}) if isinstance(j_info, dict) and "journey" in j_info else j_info
        title = journey_dict.get("title", "Chennai → Delhi → Paris Adventure") if isinstance(journey_dict, dict) else "Chennai → Delhi → Paris Adventure"

        # Extract nodes list if nested under digital twin
        if isinstance(j_info, dict) and "nodes" in j_info:
            nodes = j_info["nodes"]

        # --- Intent 1: Total Trip Expenses / Whole Journey Cost ---
        if any(term in msg_lower for term in ["whole journey", "entire trip", "total cost", "total expense", "whole trip", "all expenses", "trip cost", "trip expense", "journey expense"]):
            if nodes and isinstance(nodes, list):
                total_cost = sum(n.get("cost", 0) if isinstance(n, dict) else getattr(n, "cost", 0) or 0 for n in nodes)
                flights_cost = sum(n.get("cost", 0) if isinstance(n, dict) else getattr(n, "cost", 0) or 0 for n in nodes if (n.get("type") if isinstance(n, dict) else getattr(n, "type", "")) == "flight")
                hotels_cost = sum(n.get("cost", 0) if isinstance(n, dict) else getattr(n, "cost", 0) or 0 for n in nodes if (n.get("type") if isinstance(n, dict) else getattr(n, "type", "")) == "hotel")
                transfers_cost = sum(n.get("cost", 0) if isinstance(n, dict) else getattr(n, "cost", 0) or 0 for n in nodes if (n.get("type") if isinstance(n, dict) else getattr(n, "type", "")) in ["airport_transfer", "taxi"])
                activities_cost = sum(n.get("cost", 0) if isinstance(n, dict) else getattr(n, "cost", 0) or 0 for n in nodes if (n.get("type") if isinstance(n, dict) else getattr(n, "type", "")) == "activity")
                dining_cost = sum(n.get("cost", 0) if isinstance(n, dict) else getattr(n, "cost", 0) or 0 for n in nodes if (n.get("type") if isinstance(n, dict) else getattr(n, "type", "")) == "restaurant")

                return (
                    f"The total expense for your entire '{title}' is ₹{int(total_cost):,} across 10 booked components:\n"
                    f"• Flights (2): ₹{int(flights_cost):,}\n"
                    f"• Hotels (2): ₹{int(hotels_cost):,}\n"
                    f"• Airport Transfers (2): ₹{int(transfers_cost):,}\n"
                    f"• Sightseeing & Activities (2): ₹{int(activities_cost):,}\n"
                    f"• Dining Reservations (2): ₹{int(dining_cost):,}"
                )
            return (
                f"The total baseline cost for your complete '{title}' trip is ₹92,300. "
                f"This includes 2 flights (₹40,500), 2 hotel stays (₹39,000), transfers (₹2,675), activities (₹3,375), and fine dining (₹6,750)."
            )

        # --- Intent 2: Cheapest Recovery Strategy ---
        elif "cheapest recovery" in msg_lower or "cheapest option" in msg_lower or "lowest cost recovery" in msg_lower or "cheapest rebook" in msg_lower:
            return (
                f"Your cheapest recovery option is 'Budget Recovery (IndiGo 6E-204)' which saves ₹1,200 compared "
                f"to standard rebooking while preserving your Paris hotel and Eiffel Tower reservations."
            )

        # --- Intent 3: Flight Details & Airlines ---
        elif any(term in msg_lower for term in ["flight", "airline", "flight number", "flight details", "air india", "air france", "seat", "terminal"]):
            return (
                f"Your trip includes 2 major flights:\n"
                f"1. Air India (AI-542): Chennai (MAA) → Delhi (DEL), 06:00 - 08:30 | Seat 14A, Terminal 1 (Cost: ₹5,500)\n"
                f"2. Air France (AF-226): Delhi (DEL) → Paris (CDG), 07:00 - 13:00 | Terminal 3 (Cost: ₹35,000)\n"
                f"Flight 2 is a critical international leg with a 30-minute connection buffer."
            )

        # --- Intent 4: Hotel Accommodations ---
        elif any(term in msg_lower for term in ["hotel", "stay", "accommodation", "checkin", "check-in", "imperial", "marais", "room"]):
            return (
                f"Your trip includes 2 hotel stays:\n"
                f"1. The Imperial New Delhi: Check-in Day 1 at 10:00 AM (Deluxe Room, ₹12,000/night)\n"
                f"2. Hôtel Le Marais Paris: Check-in Day 2 at 3:00 PM (Superior Double, ₹27,000 / €180/night)\n"
                f"Both hotel stays are linked to your airport transfers via dependency rules."
            )

        # --- Intent 5: Activities & Sightseeing ---
        elif any(term in msg_lower for term in ["activity", "activities", "tour", "sightseeing", "eiffel", "red fort", "ticket"]):
            return (
                f"You have 2 scheduled activities:\n"
                f"1. Red Fort Heritage Walk (Delhi): Day 1, 14:00 - 17:00 (Ref: DHT-RF-001, ₹1,500)\n"
                f"2. Eiffel Tower Summit Visit (Paris): Day 2, 16:00 - 18:00 (Ref: ET-VIS-001, ₹1,875 / €25)\n"
                f"Both activities have medium flexibility."
            )

        # --- Intent 6: Dining & Food ---
        elif any(term in msg_lower for term in ["restaurant", "dining", "food", "dinner", "lunch", "bukhara", "comptoir", "eating"]):
            return (
                f"You have 2 fine dining reservations:\n"
                f"1. Bukhara (ITC Maurya, Delhi): Day 1 at 19:30 (North Indian, Party of 2, ₹3,000)\n"
                f"2. Le Comptoir du Panthéon (Paris): Day 2 at 20:00 (French Bistro, ₹3,750 / €50)"
            )

        # --- Intent 7: Delays & Disruptions ---
        elif any(term in msg_lower for term in ["delay", "delayed", "disruption", "cancelled", "cancellation", "late", "missed"]):
            if disruptions:
                return (
                    f"Active Disruption Alert: 1 disruption is currently logged on '{title}'. "
                    f"The Ripple Impact Engine has flagged downstream components as [Affected/At Risk]. "
                    f"Head over to the Recovery Center to approve your recommended recovery strategy."
                )
            return (
                f"If your primary flight in {title} is delayed by 4 hours, the Ripple Impact Engine "
                f"calculates that 4 downstream components (Transfer, Hotel Check-in, Sightseeing, and Dinner) "
                f"will be affected due to buffer conflicts. TripShield AI automatically generates 5 recovery options."
            )

        # --- Intent 8: Resilience Score & Risk ---
        elif any(term in msg_lower for term in ["resilience", "score", "risk", "vulnerable", "safety score"]):
            return (
                f"Your journey resilience is currently rated 78 / 100 (Resilient). "
                f"Your connection buffer score is 80%, booking flexibility is 60%, and non-refundable exposure protection is 75%."
            )

        # --- Intent 9: Preferences & Priority ---
        elif any(term in msg_lower for term in ["preference", "priority", "budget", "comfort", "speed", "change"]):
            return (
                f"Your current traveler priorities are:\n"
                f"• Speed Priority: 80%\n"
                f"• Comfort Priority: 70%\n"
                f"• Minimal Changes Priority: 60%\n"
                f"• Budget Priority: 50%\n"
                f"TripShield AI uses these exact weights to rank recovery strategies in the Recovery Center."
            )

        # --- Intent 10: Weather & Climate ---
        elif any(term in msg_lower for term in ["weather", "temperature", "rain", "forecast", "climate", "hot", "cold"]):
            return (
                f"Weather Forecast for '{title}':\n"
                f"• Delhi: 28°C, Clear Skies (Low delay risk)\n"
                f"• Paris: 18°C, Partly Cloudy (Light showers expected, 15% weather risk factor applied to Eiffel Tower visit)."
            )

        # --- Intent 11: Visa & Travel Documents ---
        elif any(term in msg_lower for term in ["visa", "passport", "document", "entry", "customs", "immigration"]):
            return (
                f"For your India (MAA/DEL) → France (CDG) journey:\n"
                f"• Schengen Visa required for entry into France (Paris).\n"
                f"• Passport validity must extend at least 3 months beyond your Paris check-out date.\n"
                f"TripShield AI stores your booking reference numbers for seamless check-in verification."
            )

        # --- Intent 12: Baggage & Luggage ---
        elif any(term in msg_lower for term in ["baggage", "luggage", "carry-on", "bag", "check-in bag"]):
            return (
                f"Baggage Allowance for '{title}':\n"
                f"• Air India (AI-542): Check-in 15 kg, Cabin 7 kg\n"
                f"• Air France (AF-226): Check-in 23 kg (1 piece), Cabin 12 kg\n"
                f"When rebooking via Recovery Center, baggage policies are automatically preserved."
            )

        # --- Intent 13: Currency & Exchange ---
        elif any(term in msg_lower for term in ["currency", "rupee", "euro", "inr", "eur", "exchange", "money"]):
            return (
                f"Currency Breakdown for '{title}':\n"
                f"• India Legs: Indian Rupee (INR ₹)\n"
                f"• France Legs: Euro (EUR €, converted at 1 EUR = ₹75 INR for budget calculation).\n"
                f"Your total journey cost is ₹92,300."
            )

        # --- Intent 14: General / Other Human Question Fallback ---
        else:
            return (
                f"I am monitoring '{title}' ({len(nodes) if nodes else 10} components, 9 dependency links). "
                f"I can answer questions about your total journey expenses (₹92,300), flight details (AI-542, AF-226), "
                f"hotels (The Imperial, Le Marais), activities (Red Fort, Eiffel Tower), weather, visa requirements, "
                f"or disruption recovery options!"
            )


class TripShieldGuardian:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def chat(self, message: str, journey_data: Dict[str, Any], disruptions: List[Any], recoveries: List[Any]) -> Dict[str, Any]:
        context = {
            "journey": journey_data,
            "disruptions": [d.__dict__ if hasattr(d, '__dict__') else d for d in disruptions] if disruptions else [],
            "recoveries": recoveries
        }
        response = self.llm.chat(message, context)
        return {
            "response": response,
            "context_used": {
                "nodes_count": len(journey_data.get("nodes", [])) if isinstance(journey_data.get("nodes"), list) else 0,
                "disruptions_count": len(disruptions),
                "recoveries_count": len(recoveries)
            }
        }
