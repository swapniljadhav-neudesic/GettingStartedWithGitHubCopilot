from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check that we get a dict of activities
    assert isinstance(activities, dict)
    
    # Verify structure of an activity
    for name, details in activities.items():
        assert isinstance(name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Try signing up for Chess Club
    email = "test@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert email in response.json()["message"]
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    
    # Try signing up again (should fail)
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up
    email = "unregister_test@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert email in response.json()["message"]
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]
    
    # Try unregistering again (should fail)
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()