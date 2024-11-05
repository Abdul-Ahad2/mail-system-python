from datetime import datetime

from server.data_manager import DataManager

class AuthManager:
    def __init__(self):
        self.data_manager = DataManager()
    
    def register(self, username, password):
        users = self.data_manager.load_data(self.data_manager.users_file) or {}
        
        if username in users:
            return False
            
        users[username] = {
            'password': password,
            'created_at': datetime.now().isoformat()
        }
        self.data_manager.save_data(self.data_manager.users_file, users)
        return True
    
    def login(self, username, password):
        users = self.data_manager.load_data(self.data_manager.users_file) or {}
        user = users.get(username)
        
        if user and user['password'] == password:
            return True
        return False
