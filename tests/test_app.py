import pytest
from fastapi.testclient import TestClient
from copy import deepcopy

import src.app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore activities to original state after each test to avoid test cross-talk."""
    orig = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(orig))


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert f"Signed up {email} for {activity}" in r.json()["message"]

    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 200
    assert f"Unregistered {email} from {activity}" in r.json()["message"]

    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_signup_duplicate_fails():
    activity = "Chess Club"
    email = "duplicate@example.com"

    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200

    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 400
    assert r.json()["detail"] == "Student is already signed up"


def test_unregister_not_signed_up_fails():
    activity = "Chess Club"
    email = "not-signed@example.com"

    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 400
    assert r.json()["detail"] == "Student is not signed up"


def test_signup_invalid_activity_returns_404():
    r = client.post("/activities/Nonexistent/signup?email=a@b.com")
    assert r.status_code == 404


def test_unregister_invalid_activity_returns_404():
    r = client.post("/activities/Nonexistent/unregister?email=a@b.com")
    assert r.status_code == 404


def test_signup_missing_email_returns_422():
    r = client.post("/activities/Chess%20Club/signup")
    assert r.status_code == 422
