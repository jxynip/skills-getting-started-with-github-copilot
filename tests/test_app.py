import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activity_list():
    # Arrange / Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert "Gym Club" not in payload
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity = "Art Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    email = "unknown@student.edu"

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_existing_student():
    # Arrange
    activity = "Chess Club"
    email = "temp.student@mergington.edu"
    activities[activity]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "missing@student.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
