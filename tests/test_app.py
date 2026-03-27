import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_returns_all_activities(self):
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == len(activities)

    def test_activity_has_required_fields(self):
        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_successful_signup(self):
        # Arrange
        email = "alice@mergington.edu"

        # Act
        response = client.post("/activities/Soccer Team/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_participant_added_to_activity(self):
        # Arrange
        email = "alice@mergington.edu"

        # Act
        client.post("/activities/Soccer Team/signup", params={"email": email})

        # Assert
        assert email in activities["Soccer Team"]["participants"]

    def test_duplicate_signup_returns_400(self):
        # Arrange
        email = "new@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})

        # Act
        response = client.post("/activities/Chess Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_duplicate_signup_case_insensitive(self):
        # Arrange — michael@mergington.edu is already a Chess Club participant

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "MICHAEL@mergington.edu"},
        )

        # Assert
        assert response.status_code == 400

    def test_unknown_activity_returns_404(self):
        # Arrange
        email = "alice@mergington.edu"

        # Act
        response = client.post("/activities/Nonexistent Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_full_activity_returns_400(self):
        # Arrange
        activity = activities["Chess Club"]
        activity["participants"] = [
            f"student{i}@mergington.edu" for i in range(activity["max_participants"])
        ]

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "overflow@mergington.edu"},
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_email_stored_as_lowercase(self):
        # Arrange
        mixed_case_email = "Alice@Mergington.EDU"

        # Act
        client.post("/activities/Soccer Team/signup", params={"email": mixed_case_email})

        # Assert
        assert "alice@mergington.edu" in activities["Soccer Team"]["participants"]


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_successful_unregister(self):
        # Arrange — michael@mergington.edu is already a Chess Club participant

        # Act
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )

        # Assert
        assert response.status_code == 200
        assert "michael@mergington.edu" in response.json()["message"]

    def test_participant_removed_from_activity(self):
        # Arrange — michael@mergington.edu is already a Chess Club participant

        # Act
        client.delete("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

        # Assert
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_non_participant_returns_404(self):
        # Arrange
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete("/activities/Chess Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_unregister_unknown_activity_returns_404(self):
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.delete("/activities/Nonexistent Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_unregister_case_insensitive(self):
        # Arrange — michael@mergington.edu is already a Chess Club participant

        # Act
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "MICHAEL@mergington.edu"},
        )

        # Assert
        assert response.status_code == 200
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

