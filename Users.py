"""
users.py - User management for Ollama Proxy Server

This module provides user management functionality separate from the main application.
In a production environment, this should be replaced with a proper database.
"""

from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

# Default users if no user file exists
DEFAULT_USERS = {
    "admin": {
        "password_hash": generate_password_hash("admin123"),
        "role": "admin"
    }
}

class UserManager:
    """Manages users, authentication, and authorization"""
    
    def __init__(self, user_file="users.json"):
        """Initialize the user manager"""
        self.user_file = user_file
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from file or use defaults"""
        if os.path.exists(self.user_file):
            try:
                with open(self.user_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
                return DEFAULT_USERS
        return DEFAULT_USERS
    
    def _save_users(self):
        """Save users to file"""
        try:
            with open(self.user_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def authenticate(self, username, password):
        """Authenticate a user"""
        if username in self.users:
            if check_password_hash(self.users[username]["password_hash"], password):
                return True
        return False
    
    def get_user_role(self, username):
        """Get a user's role"""
        if username in self.users:
            return self.users[username].get("role", "user")
        return None
    
    def add_user(self, username, password, role="user"):
        """Add a new user"""
        if username in self.users:
            return False, "User already exists"
        
        self.users[username] = {
            "password_hash": generate_password_hash(password),
            "role": role
        }
        
        if self._save_users():
            return True, "User added successfully"
        return False, "Failed to save users"
    
    def delete_user(self, username):
        """Delete a user"""
        if username not in self.users:
            return False, "User does not exist"
        
        del self.users[username]
        
        if self._save_users():
            return True, "User deleted successfully"
        return False, "Failed to save users"
    
    def update_password(self, username, password):
        """Update a user's password"""
        if username not in self.users:
            return False, "User does not exist"
        
        self.users[username]["password_hash"] = generate_password_hash(password)
        
        if self._save_users():
            return True, "Password updated successfully"
        return False, "Failed to save users"
    
    def update_role(self, username, role):
        """Update a user's role"""
        if username not in self.users:
            return False, "User does not exist"
        
        self.users[username]["role"] = role
        
        if self._save_users():
            return True, "Role updated successfully"
        return False, "Failed to save users"
    
    def get_all_users(self):
        """Get all usernames and their roles"""
        return {username: data.get("role", "user") for username, data in self.users.items()}

# Example usage
if __name__ == "__main__":
    # Initialize user manager
    user_manager = UserManager()
    
    # Add a user
    success, message = user_manager.add_user("testuser", "password123")
    print(f"Adding user: {message}")
    
    # Authenticate a user
    if user_manager.authenticate("testuser", "password123"):
        print("Authentication successful")
    else:
        print("Authentication failed")
    
    # Get a user's role
    role = user_manager.get_user_role("testuser")
    print(f"User role: {role}")
