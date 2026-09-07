from typing import List, Dict, Any
from app.providers.base import (
    FlightProvider, HotelProvider, TransportProvider, ActivityProvider, WeatherProvider,
    FlightOption, HotelOption, TransportOption, ActivityOption, WeatherForecast
)
import random

class MockFlightProvider(FlightProvider):
    def search_flights(self, origin: str, destination: str, date: str, preferences: Dict[str, Any]) -> List[FlightOption]:
        airlines = ["Air India", "IndiGo", "SpiceJet", "Vistara", "Air France"]
        return [
            FlightOption(
                airline=random.choice(airlines),
                flight_number=f"{random.randint(100, 999)}",
                price=random.uniform(3000, 25000),
                departure_time=f"{date}T10:00:00",
                arrival_time=f"{date}T12:00:00",
                duration_mins=120
            ) for _ in range(3)
        ]

class MockHotelProvider(HotelProvider):
    def search_hotels(self, location: str, checkin: str, checkout: str, preferences: Dict[str, Any]) -> List[HotelOption]:
        return [
            HotelOption("Grand Hotel", 12000.0, 4.5, "City Center"),
            HotelOption("Budget Inn", 3000.0, 3.0, "Suburbs"),
        ]

class MockTransportProvider(TransportProvider):
    def search_transport(self, origin: str, destination: str, datetime: str, type: str) -> List[TransportOption]:
        return [
            TransportOption("taxi", "Uber", 800.0, 45)
        ]

class MockActivityProvider(ActivityProvider):
    def search_activities(self, location: str, date: str, type: str) -> List[ActivityOption]:
        return [
            ActivityOption("City Tour", 1500.0, 180)
        ]

class MockWeatherProvider(WeatherProvider):
    def get_forecast(self, location: str, date: str) -> WeatherForecast:
        return WeatherForecast("Sunny", 25.0, 10)
