import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from server.auth_manager import AuthManager
from server.data_manager import DataManager

class TestAuthManager:
    @pytest.fixture
    def auth_manager(self):
        """Create a fresh AuthManager for each test"""
        # Create a temporary test users file
        test_data_dir = Path(base_dir) / "tests" / "test_data"
        test_data_dir.mkdir(exist_ok=True)
        test_users_file = test_data_dir / "test_users.json"
        
        # Patch DataManager to use test file
        data_manager = DataManager()
        data_manager.users_file = test_users_file
        
        # Clear any existing test data
        if test_users_file.exists():
            os.remove(test_users_file)
        
        # Create auth manager with test data manager
        auth_manager = AuthManager()
        auth_manager.data_manager = data_manager
        
        yield auth_manager
        
        # Cleanup
        if test_users_file.exists():
            os.remove(test_users_file)
    
    def test_register_new_user(self, auth_manager):
        """Test registering a new user"""
        result = auth_manager.register("testuser", "password123")
        assert result is True, "Registration of new user should succeed"
    
    def test_register_duplicate_user(self, auth_manager):
        """Test registering a user with an existing username"""
        # First registration
        auth_manager.register("testuser", "password123")
        
        # Second registration with same username
        result = auth_manager.register("testuser", "differentpassword")
        assert result is False, "Registration with duplicate username should fail"
    
    def test_login_valid_credentials(self, auth_manager):
        """Test login with valid credentials"""
        # First register the user
        auth_manager.register("testuser", "password123")
        
        # Then attempt login
        result = auth_manager.login("testuser", "password123")
        assert result is True, "Login with correct credentials should succeed"
    
    def test_login_invalid_username(self, auth_manager):
        """Test login with non-existent username"""
        result = auth_manager.login("nonexistentuser", "password")
        assert result is False, "Login with non-existent username should fail"
    
    def test_login_invalid_password(self, auth_manager):
        """Test login with incorrect password"""
        # First register the user
        auth_manager.register("testuser", "password123")
        
        # Then attempt login with wrong password
        result = auth_manager.login("testuser", "wrongpassword")
        assert result is False, "Login with incorrect password should fail"
    
    def test_multiple_user_registration(self, auth_manager):
        """Test registering multiple unique users"""
        users = [
            ("user1", "pass1"),
            ("user2", "pass2"),
            ("user3", "pass3")
        ]
        
        # Register multiple users
        for username, password in users:
            result = auth_manager.register(username, password)
            assert result is True, f"Registration for {username} should succeed"
        
        # Verify logins
        for username, password in users:
            result = auth_manager.login(username, password)
            assert result is True, f"Login for {username} should succeed"
