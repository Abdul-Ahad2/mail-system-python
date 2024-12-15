import pytest
import os
import sys
import json
from pathlib import Path

# Add project root to Python path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from server.data_manager import DataManager

class TestDataManager:
    @pytest.fixture
    def test_data_dir(self):
        """Create a temporary test data directory"""
        test_dir = Path(base_dir) / "tests" / "test_data"
        test_dir.mkdir(exist_ok=True)
        yield test_dir
        
        # Cleanup: remove test files
        for file in test_dir.glob("*"):
            file.unlink()
        test_dir.rmdir()
    
    @pytest.fixture
    def data_manager(self, test_data_dir):
        """Create a DataManager with test data directory"""
        data_manager = DataManager()
        data_manager.data_dir = test_data_dir
        data_manager.users_file = test_data_dir / "users.json"
        data_manager.emails_file = test_data_dir / "emails.json"
        data_manager.queue_file = test_data_dir / "queue.json"
        return data_manager
    
    def test_save_and_load_data(self, data_manager):
        """Test saving and loading data"""
        test_data = {
            "users": {
                "testuser": {
                    "password": "testpass",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }
        
        # Save data
        data_manager.save_data(data_manager.users_file, test_data["users"])
        
        # Load data
        loaded_data = data_manager.load_data(data_manager.users_file)
        
        assert loaded_data == test_data["users"], "Loaded data should match saved data"
    
    def test_save_overwrite_data(self, data_manager):
        """Test overwriting existing data"""
        initial_data = {"key1": "value1"}
        updated_data = {"key2": "value2"}
        
        # Save initial data
        data_manager.save_data(data_manager.users_file, initial_data)
        
        # Overwrite with new data
        data_manager.save_data(data_manager.users_file, updated_data)
        
        # Load and verify
        loaded_data = data_manager.load_data(data_manager.users_file)
        assert loaded_data == updated_data, "Data should be completely replaced"
    
  
