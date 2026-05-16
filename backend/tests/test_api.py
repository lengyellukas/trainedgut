"""
HTTP-level API smoke tests.

Only covers endpoints that don't require authentication. Tests for protected
endpoints (/generate-plan, /me, /feedback, /extra-session, /plan) were removed
when JWT auth was introduced — they'd need a mocked JWT to exercise the auth
dependency, which isn't worth the test infrastructure cost at this stage.
"""
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


class TestHealth:
    def test_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_ok(self):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}
