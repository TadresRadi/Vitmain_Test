"""
Locust performance test for Vitmain API.

Run with:
    locust -f locustfile.py --host=http://localhost:8000

Then open http://localhost:8089 in your browser to configure and run the test.
"""
from locust import HttpUser, task, between


class VitmainAPIUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Login at the start of each user session."""
        # Create a test user first (or use an existing one)
        response = self.client.post("/api/auth/login", json={
            "email": "perf-test@example.com",
            "password": "TestPass123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access")
        else:
            self.token = None

    @task(3)
    def view_plans(self):
        """View pricing plans — most common endpoint."""
        self.client.get("/api/plans")

    @task(2)
    def health_check(self):
        """Health check — lightweight."""
        self.client.get("/health/")

    @task(1)
    def view_profile(self):
        """View user profile — requires auth."""
        if self.token:
            self.client.get(
                "/api/users/profile",
                headers={"Authorization": f"Bearer {self.token}"}
            )

    @task(1)
    def view_subscription_status(self):
        """View subscription status — requires auth."""
        if self.token:
            self.client.get(
                "/api/subscription/status",
                headers={"Authorization": f"Bearer {self.token}"}
            )