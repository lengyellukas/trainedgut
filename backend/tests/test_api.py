import pytest
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

VALID_PAYLOAD = {
    "body_weight_kg": 75,
    "sport_type": "triathlon",
    "target_race_time_hours": 12.0,
    "race_date": "2026-09-20",
    "start_preference": "immediately",
    "preferred_start_date": None,
    "carb_tolerance_option": "never_used",
    "gi_history": "occasional",
    "long_sessions": [
        {"duration_option": "2h_to_3h"},
        {"duration_option": "over_6h"},
    ],
}


class TestHealth:
    def test_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_ok(self):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


class TestGeneratePlan:
    def test_valid_request_returns_200(self):
        response = client.post("/generate-plan", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_valid_request_returns_valid_status(self):
        response = client.post("/generate-plan", json=VALID_PAYLOAD)
        assert response.json()["status"] == "valid"

    def test_valid_request_includes_plan(self):
        response = client.post("/generate-plan", json=VALID_PAYLOAD)
        assert response.json()["plan"] is not None

    def test_plan_has_weeks(self):
        response = client.post("/generate-plan", json=VALID_PAYLOAD)
        plan = response.json()["plan"]
        assert len(plan["weeks"]) > 0

    def test_plan_has_gel_package(self):
        response = client.post("/generate-plan", json=VALID_PAYLOAD)
        plan = response.json()["plan"]
        assert "gel_package" in plan
        assert plan["gel_package"]["total_gels"] > 0

    def test_too_short_returns_200_not_error(self):
        payload = {**VALID_PAYLOAD, "race_date": "2026-05-10"}  # only days away
        response = client.post("/generate-plan", json=payload)
        assert response.status_code == 200

    def test_too_short_has_correct_status(self):
        payload = {**VALID_PAYLOAD, "race_date": "2026-05-10"}
        response = client.post("/generate-plan", json=payload)
        assert response.json()["status"] == "too_short"

    def test_too_short_plan_is_null(self):
        payload = {**VALID_PAYLOAD, "race_date": "2026-05-10"}
        response = client.post("/generate-plan", json=payload)
        assert response.json()["plan"] is None

    def test_missing_required_field_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "race_date"}
        response = client.post("/generate-plan", json=payload)
        assert response.status_code == 422

    def test_invalid_enum_value_returns_422(self):
        payload = {**VALID_PAYLOAD, "sport_type": "underwater_hockey"}
        response = client.post("/generate-plan", json=payload)
        assert response.status_code == 422

    def test_invalid_date_format_returns_422(self):
        payload = {**VALID_PAYLOAD, "race_date": "20-09-2026"}
        response = client.post("/generate-plan", json=payload)
        assert response.status_code == 422

    def test_all_sport_types_are_accepted(self):
        sports = [
            "running", "triathlon",
            "cycling",
            "obstacle_race", "duathlon", "swimming",
        ]
        for sport in sports:
            payload = {**VALID_PAYLOAD, "sport_type": sport}
            response = client.post("/generate-plan", json=payload)
            assert response.status_code == 200, f"sport_type={sport} failed"

    def test_starts_late_returns_valid_plan(self):
        # OPTIMAL start for a far-future race will be after today
        payload = {**VALID_PAYLOAD, "start_preference": "optimal", "race_date": "2027-06-01"}
        response = client.post("/generate-plan", json=payload)
        data = response.json()
        assert data["status"] == "starts_late"
        assert data["plan"] is not None
