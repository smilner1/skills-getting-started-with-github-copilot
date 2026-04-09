import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that activities endpoint returns a dictionary"""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities include Chess Club and Programming Class"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert all(activity in activities_data for activity in expected_activities)
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for name, details in activities_data.items():
            assert required_fields.issubset(details.keys()), f"Missing fields in {name}"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, sample_activity, sample_email):
        """Test successful signup for an activity"""
        # Arrange
        activities[sample_activity]["participants"] = []
        
        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert sample_email in activities[sample_activity]["participants"]
        assert "Signed up" in response.json()["message"]
    
    def test_signup_activity_not_found(self, client, sample_email):
        """Test signup for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client, sample_activity):
        """Test that a student cannot signup twice for the same activity"""
        # Arrange
        email = "duplicate@mergington.edu"
        activities[sample_activity]["participants"] = [email]
        
        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_with_special_characters_in_email(self, client, sample_activity):
        """Test signup with special characters in email"""
        # Arrange
        activities[sample_activity]["participants"] = []
        email = "test+tag@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[sample_activity]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, sample_activity):
        """Test successful unregister from an activity"""
        # Arrange
        email = "unregister@mergington.edu"
        activities[sample_activity]["participants"] = [email]
        
        # Act
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in activities[sample_activity]["participants"]
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_activity_not_found(self, client, sample_email):
        """Test unregister from non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_registered(self, client, sample_activity, sample_email):
        """Test unregister when student is not registered"""
        # Arrange
        activities[sample_activity]["participants"] = []
        
        # Act
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestActivityCapacity:
    """Tests for activity capacity management"""
    
    def test_activity_has_max_participants(self, client):
        """Test that activities define max_participants"""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for name, details in activities_data.items():
            assert "max_participants" in details
            assert isinstance(details["max_participants"], int)
            assert details["max_participants"] > 0
    
    def test_available_spots_calculation(self, client):
        """Test that available spots are calculated correctly"""
        # Arrange
        response = client.get("/activities")
        activities_data = response.json()
        
        # Act & Assert
        for name, details in activities_data.items():
            max_participants = details["max_participants"]
            current_participants = len(details["participants"])
            available_spots = max_participants - current_participants
            
            assert available_spots >= 0, f"{name} has over-capacity"
            assert available_spots <= max_participants
