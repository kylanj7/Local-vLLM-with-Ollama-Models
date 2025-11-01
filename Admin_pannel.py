"""
admin_panel.py - Extension for the Ollama Proxy Server

This file shows how to implement an admin panel for user management.
It can be integrated into the main application.
"""

from flask import render_template_string, request, redirect, url_for, flash, session
from functools import wraps

# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# Admin panel template
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ollama Proxy - Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        table, th, td { border: 1px solid #ddd; }
        th, td { padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .actions { display: flex; gap: 10px; }
        .btn { padding: 5px 10px; text-decoration: none; color: white; border-radius: 3px; display: inline-block; }
        .btn-primary { background-color: #4CAF50; }
        .btn-danger { background-color: #f44336; }
        .btn-info { background-color: #2196F3; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 8px; box-sizing: border-box; }
        .alert { padding: 10px; margin-bottom: 15px; border-radius: 3px; }
        .alert-success { background-color: #d4edda; color: #155724; }
        .alert-danger { background-color: #f8d7da; color: #721c24; }
        .user-info { text-align: right; margin-bottom: 20px; }
        .user-info a { color: #666; text-decoration: none; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="user-info">
        Logged in as {{ session.username }} | <a href="{{ url_for('home') }}">Home</a> | <a href="{{ url_for('logout') }}">Logout</a>
    </div>

    <h1>Admin Panel</h1>
    
    {% if message %}
    <div class="alert alert-{{ message_type }}">{{ message }}</div>
    {% endif %}
    
    <h2>User Management</h2>
    
    <h3>Add New User</h3>
    <form method="post" action="{{ url_for('admin_add_user') }}">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="form-group">
            <label for="role">Role:</label>
            <select id="role" name="role">
                <option value="user">User</option>
                <option value="admin">Admin</option>
            </select>
        </div>
        
        <button type="submit" class="btn btn-primary">Add User</button>
    </form>
    
    <h3>Current Users</h3>
    <table>
        <thead>
            <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for username, role in users.items() %}
            <tr>
                <td>{{ username }}</td>
                <td>{{ role }}</td>
                <td class="actions">
                    <a href="{{ url_for('admin_edit_user', username=username) }}" class="btn btn-info">Edit</a>
                    <form method="post" action="{{ url_for('admin_delete_user', username=username) }}" 
                          onsubmit="return confirm('Are you sure you want to delete this user?');" style="display:inline">
                        <button type="submit" class="btn btn-danger">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <h2>System Information</h2>
    <table>
        <tr>
            <td><strong>Ollama Status:</strong></td>
            <td>{{ ollama_status }}</td>
        </tr>
        <tr>
            <td><strong>Available Models:</strong></td>
            <td>{{ available_models|join(', ') }}</td>
        </tr>
    </table>
</body>
</html>
'''

# User edit template
USER_EDIT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ollama Proxy - Edit User</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; margin-right: 10px; }
        .btn-secondary { background: #6c757d; }
        .user-info { text-align: right; margin-bottom: 20px; }
        .user-info a { color: #666; text-decoration: none; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="user-info">
        Logged in as {{ session.username }} | <a href="{{ url_for('admin_panel') }}">Back to Admin</a> | <a href="{{ url_for('logout') }}">Logout</a>
    </div>

    <h1>Edit User: {{ edit_username }}</h1>
    
    <form method="post" action="{{ url_for('admin_update_user', username=edit_username) }}">
        <div class="form-group">
            <label for="role">Role:</label>
            <select id="role" name="role">
                <option value="user" {% if current_role == 'user' %}selected{% endif %}>User</option>
                <option value="admin" {% if current_role == 'admin' %}selected{% endif %}>Admin</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="password">New Password (leave empty to keep current):</label>
            <input type="password" id="password" name="password">
        </div>
        
        <div>
            <button type="submit">Update User</button>
            <a href="{{ url_for('admin_panel') }}" class="btn btn-secondary" style="text-decoration: none; display: inline-block;">Cancel</a>
        </div>
    </form>
</body>
</html>
'''

# How to integrate these routes into your main application:

'''
# Import the user manager
from users import UserManager

# Initialize the user manager
user_manager = UserManager()

# Add the admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    # Get Ollama status
    try:
        ollama_response = requests.get('http://localhost:11434/api/tags')
        ollama_status = "Running" if ollama_response.status_code == 200 else "Not responding"
        available_models = [model['name'] for model in ollama_response.json().get('models', [])]
    except:
        ollama_status = "Not running"
        available_models = []
    
    # Get all users
    users = user_manager.get_all_users()
    
    return render_template_string(
        ADMIN_TEMPLATE, 
        users=users, 
        ollama_status=ollama_status,
        available_models=available_models,
        message=session.pop('message', None),
        message_type=session.pop('message_type', 'info')
    )

@app.route('/admin/user/add', methods=['POST'])
@login_required
@admin_required
def admin_add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    success, message = user_manager.add_user(username, password, role)
    session['message'] = message
    session['message_type'] = 'success' if success else 'danger'
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/edit/<username>')
@login_required
@admin_required
def admin_edit_user(username):
    # Get user role
    role = user_manager.get_user_role(username)
    
    return render_template_string(
        USER_EDIT_TEMPLATE,
        edit_username=username,
        current_role=role
    )

@app.route('/admin/user/update/<username>', methods=['POST'])
@login_required
@admin_required
def admin_update_user(username):
    role = request.form.get('role')
    password = request.form.get('password')
    
    # Update role
    if role:
        user_manager.update_role(username, role)
    
    # Update password if provided
    if password:
        user_manager.update_password(username, password)
    
    session['message'] = f"User {username} updated successfully"
    session['message_type'] = 'success'
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/delete/<username>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(username):
    # Prevent deleting your own account
    if username == session['username']:
        session['message'] = "You cannot delete your own account"
        session['message_type'] = 'danger'
    else:
        success, message = user_manager.delete_user(username)
        session['message'] = message
        session['message_type'] = 'success' if success else 'danger'
    
    return redirect(url_for('admin_panel'))
'''
