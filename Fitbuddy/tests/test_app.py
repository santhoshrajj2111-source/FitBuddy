import os


os.environ["DEMO_MODE"] = "true"

os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_fitbuddy.db"

os.environ[
    "ADMIN_KEY"
] = "test-admin-key"


from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


init_db()

client = TestClient(app)


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_generate_plan():

    response = client.post(
        "/generate-workout",
        data={
            "name": "Test User",
            "user_id": "test01",
            "age": "25",
            "weight": "70",
            "goal": "muscle gain",
            "intensity": "medium",
        },
    )

    assert response.status_code == 200

    assert "7-Day Workout Plan" in response.text

    assert "Test User" in response.text


def test_feedback_update():

    response = client.post(
        "/submit-feedback",
        data={
            "user_id": "test01",
            "feedback":
                "Add more cardio and one extra recovery day."
        },
    )

    assert response.status_code == 200

    assert "updated successfully" in response.text.lower()


def test_admin_api_requires_key():

    response = client.get(
        "/api/users"
    )

    assert response.status_code == 401


def test_admin_api_with_key():

    response = client.get(
        "/api/users?key=test-admin-key"
    )

    assert response.status_code == 200

    assert any(
        item["user_id"] == "test01"
        for item in response.json()
    )