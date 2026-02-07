"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Save original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Swimming Club": {
            "description": "Swimming training and water sports",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Studio": {
            "description": "Express creativity through painting and drawing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater arts and performance training",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Learn public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original)
    yield
    # Reset after test
    activities.clear()
    activities.update(original)


def test_root_redirect(client):
    """Test that root redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9  # Should have 9 activities


def test_signup_success(client):
    """Test successful signup"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]


def test_signup_duplicate_student(client):
    """Test that duplicate signup is prevented"""
    email = "michael@mergington.edu"
    
    # Try to signup again (already in participants)
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_success(client):
    """Test successful unregister"""
    email = "michael@mergington.edu"
    
    # Verify student is registered
    activities_data = client.get("/activities").json()
    assert email in activities_data["Chess Club"]["participants"]
    
    # Unregister
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify student is no longer registered
    activities_data = client.get("/activities").json()
    assert email not in activities_data["Chess Club"]["participants"]


def test_unregister_not_registered(client):
    """Test unregister when student is not registered"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_unregister_nonexistent_activity(client):
    """Test unregister from non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_signup_and_unregister_flow(client):
    """Test complete signup and unregister flow"""
    email = "newstudent@mergington.edu"
    activity = "Basketball Team"
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify registered
    activities_data = client.get("/activities").json()
    assert email in activities_data[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify unregistered
    activities_data = client.get("/activities").json()
    assert email not in activities_data[activity]["participants"]
