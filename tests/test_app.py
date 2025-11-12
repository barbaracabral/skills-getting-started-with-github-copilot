from fastapi.testclient import TestClient
import os
import sys
from pathlib import Path

# Ensure src directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app

client = TestClient(app)


def test_root_redirect_shows_index():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Mergington High School" in resp.text


def test_get_activities_contains_known_activity():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_duplicate_and_unregister_flow():
    activity = "Chess Club"
    email = "tester+pytest@example.com"

    # Ensure signup works
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email} for {activity}" in resp.json().get("message", "")

    # Duplicate signup should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Unregister should succeed
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert f"Unregistered {email} from {activity}" in resp.json().get("message", "")

    # Unregistering again should return 404
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404


def test_activity_not_found_cases():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "x@example.com"})
    assert resp.status_code == 404

    resp = client.delete("/activities/Nonexistent/participants", params={"email": "x@example.com"})
    assert resp.status_code == 404
