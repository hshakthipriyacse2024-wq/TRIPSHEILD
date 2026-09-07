from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        pass
        
    @abstractmethod
    def explain_recovery(self, strategy: Dict[str, Any], impact: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        pass
        
    @abstractmethod
    def chat(self, message: str, journey_context: Dict[str, Any]) -> str:
        pass
