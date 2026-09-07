"""End-to-end integration test verifying full disruption to recovery flow."""
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

class TestE2EFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_full_disruption_recovery_workflow(self):
        client = TestClient(app)

        # 1. Register user
        email = f"test_e2e_user@example.com"
        reg_res = client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Test Traveler"
        })
        # Handle 200 or 201 for registration, or login if user exists
        if reg_res.status_code == 400:
            log_res = client.post("/api/v1/auth/login", json={
                "email": email,
                "password": "Password123!"
            })
            token = log_res.json()["access_token"]
        else:
            self.assertIn(reg_res.status_code, [200, 201])
            token = reg_res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Load demo journey (Chennai -> Delhi -> Paris)
        load_res = client.post("/api/v1/demo/load", headers=headers)
        self.assertEqual(load_res.status_code, 200)
        demo_data = load_res.json()
        journey_id = demo_data["journey_id"]
        self.assertEqual(demo_data["nodes_count"], 10)
        self.assertEqual(demo_data["dependencies_count"], 9)

        # 3. Get Digital Twin graph
        twin_res = client.get(f"/api/v1/journeys/{journey_id}/digital-twin", headers=headers)
        self.assertEqual(twin_res.status_code, 200)
        twin_data = twin_res.json()
        self.assertEqual(len(twin_data["nodes"]), 10)

        # 4. Simulate 4-hour flight delay
        sim_res = client.post("/api/v1/demo/simulate-delay", headers=headers)
        self.assertEqual(sim_res.status_code, 200)
        sim_data = sim_res.json()
        self.assertGreater(sim_data["impact"]["impact_score"], 0)
        self.assertGreaterEqual(len(sim_data["recovery_strategies"]), 3)

        # 5. Fetch recovery options
        rec_res = client.post(f"/api/v1/recovery/journeys/{journey_id}/recovery-options", headers=headers)
        self.assertEqual(rec_res.status_code, 200)
        strategies = rec_res.json()
        strategy_id = strategies[0]["id"]

        # 6. Approve recovery strategy
        app_res = client.post(f"/api/v1/recovery/{strategy_id}/approve", headers=headers)
        self.assertEqual(app_res.status_code, 200)

        # 7. Execute recovery strategy
        exec_res = client.post(f"/api/v1/recovery/{strategy_id}/execute", headers=headers)
        self.assertEqual(exec_res.status_code, 200)
        exec_data = exec_res.json()
        self.assertEqual(exec_data["journey_status"], "recovered")
        self.assertGreater(exec_data["resilience_score"], 0)

        # 8. Verify Journey status is now recovered in Digital Twin
        final_twin = client.get(f"/api/v1/journeys/{journey_id}/digital-twin", headers=headers)
        self.assertEqual(final_twin.status_code, 200)
        self.assertEqual(final_twin.json()["journey"]["status"], "recovered")


if __name__ == "__main__":
    unittest.main()
