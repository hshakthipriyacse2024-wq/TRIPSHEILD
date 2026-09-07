"""Unit tests for TripShield AI core engines using standard unittest."""
import unittest
from datetime import datetime, timedelta

from app.engines.ripple_impact import RippleImpactEngine
from app.engines.recovery_optimizer import RecoveryOptimizer
from app.engines.resilience_scorer import ResilienceScorer


class DummyNode:
    def __init__(self, id, type, provider, start_time, end_time, cost=1000.0, flexibility="low", importance="high"):
        self.id = id
        self.type = type
        self.provider = provider
        self.start_time = start_time
        self.end_time = end_time
        self.cost = cost
        self.currency = "INR"
        self.flexibility = flexibility
        self.importance = importance


class DummyDependency:
    def __init__(self, source_node_id, target_node_id, buffer_minutes=60, is_critical=True):
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.buffer_minutes = buffer_minutes
        self.is_critical = is_critical


class DummyJourney:
    def __init__(self, id):
        self.id = id
        self.title = "Test Trip"


class DummyDisruption:
    def __init__(self, id, affected_node_id, delay_minutes=240):
        self.id = id
        self.journey_id = "j1"
        self.affected_node_id = affected_node_id
        self.delay_minutes = delay_minutes


class TestCoreEngines(unittest.TestCase):

    def test_ripple_impact_engine(self):
        engine = RippleImpactEngine()
        now = datetime.utcnow()
        n1 = DummyNode("n1", "flight", "Air India", now, now + timedelta(hours=2), cost=5000)
        n2 = DummyNode("n2", "airport_transfer", "Uber", now + timedelta(hours=2, minutes=30), now + timedelta(hours=3), cost=800)
        n3 = DummyNode("n3", "hotel", "The Imperial", now + timedelta(hours=3, minutes=15), now + timedelta(days=1), cost=12000)

        nodes = [n1, n2, n3]
        deps = [
            DummyDependency("n1", "n2", buffer_minutes=30, is_critical=True),
            DummyDependency("n2", "n3", buffer_minutes=15, is_critical=False),
        ]

        journey = DummyJourney("j1")
        disruption = DummyDisruption("d1", affected_node_id="n1", delay_minutes=240)

        impact = engine.calculate_impact(disruption, journey, nodes, deps)

        self.assertGreater(impact.impact_score, 0)
        self.assertIn("n2", impact.directly_affected)
        self.assertIn("n3", impact.indirectly_affected)
        self.assertGreater(impact.financial_exposure, 0)

    def test_recovery_optimizer(self):
        optimizer = RecoveryOptimizer()
        now = datetime.utcnow()
        n1 = DummyNode("n1", "flight", "Air India", now, now + timedelta(hours=2), cost=5000)
        n2 = DummyNode("n2", "hotel", "The Imperial", now + timedelta(hours=3), now + timedelta(days=1), cost=12000)

        nodes = [n1, n2]
        deps = [DummyDependency("n1", "n2", buffer_minutes=60)]
        journey = DummyJourney("j1")
        disruption = DummyDisruption("d1", affected_node_id="n1", delay_minutes=240)

        strategies = optimizer.generate_strategies(disruption, None, journey, nodes, deps, None, None)

        self.assertGreaterEqual(len(strategies), 3)
        self.assertTrue(strategies[0]["is_recommended"])
        self.assertGreater(strategies[0]["overall_score"], 0)
        self.assertIn("actions", strategies[0])

    def test_resilience_scorer(self):
        scorer = ResilienceScorer()
        now = datetime.utcnow()
        n1 = DummyNode("n1", "flight", "Air India", now, now + timedelta(hours=2), cost=5000)
        n2 = DummyNode("n2", "hotel", "The Imperial", now + timedelta(hours=4), now + timedelta(days=1), cost=12000)

        nodes = [n1, n2]
        deps = [DummyDependency("n1", "n2", buffer_minutes=120)]
        journey = DummyJourney("j1")

        res = scorer.calculate_score(journey, nodes, deps)

        self.assertGreaterEqual(res["score"], 0)
        self.assertLessEqual(res["score"], 100)
        self.assertIn("classification", res)
        self.assertIn("breakdown", res)


if __name__ == "__main__":
    unittest.main()
