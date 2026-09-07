from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class FlightOption:
    airline: str
    flight_number: str
    price: float
    departure_time: str
    arrival_time: str
    duration_mins: int

@dataclass
class HotelOption:
    name: str
    price: float
    rating: float
    location: str

@dataclass
class TransportOption:
    type: str
    provider: str
    price: float
    duration_mins: int

@dataclass
class ActivityOption:
    name: str
    price: float
    duration_mins: int

@dataclass
class WeatherForecast:
    condition: str
    temp_c: float
    precipitation_chance: int

class FlightProvider(ABC):
    @abstractmethod
    def search_flights(self, origin: str, destination: str, date: str, preferences: Dict[str, Any]) -> List[FlightOption]:
        pass

class HotelProvider(ABC):
    @abstractmethod
    def search_hotels(self, location: str, checkin: str, checkout: str, preferences: Dict[str, Any]) -> List[HotelOption]:
        pass

class TransportProvider(ABC):
    @abstractmethod
    def search_transport(self, origin: str, destination: str, datetime: str, type: str) -> List[TransportOption]:
        pass

class ActivityProvider(ABC):
    @abstractmethod
    def search_activities(self, location: str, date: str, type: str) -> List[ActivityOption]:
        pass

class WeatherProvider(ABC):
    @abstractmethod
    def get_forecast(self, location: str, date: str) -> WeatherForecast:
        pass
