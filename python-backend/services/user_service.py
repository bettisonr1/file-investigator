"""
User service - handles business logic for user operations
In a real application, this would interact with a database
"""

# Mock database
users_db = {
    1: {'id': 1, 'name': 'Alice Smith', 'email': 'alice@example.com'},
    2: {'id': 2, 'name': 'Bob Johnson', 'email': 'bob@example.com'},
    3: {'id': 3, 'name': 'Charlie Brown', 'email': 'charlie@example.com'}
}
next_user_id = 4

def get_user(user_id):
    """
    Retrieve a user by ID
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        dict: User data if found, None otherwise
    """
    return users_db.get(user_id)

def create_user(name, email):
    """
    Create a new user
    
    Args:
        name: The user's name
        email: The user's email
        
    Returns:
        dict: The newly created user
    """
    global next_user_id
    
    user = {
        'id': next_user_id,
        'name': name,
        'email': email
    }
    users_db[next_user_id] = user
    next_user_id += 1
    
    return user

def update_user(user_id, data):
    """
    Update an existing user
    
    Args:
        user_id: The ID of the user to update
        data: Dictionary containing fields to update
        
    Returns:
        dict: Updated user data if found, None otherwise
    """
    if user_id not in users_db:
        return None
    
    user = users_db[user_id]
    
    # Update only provided fields
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    
    return user

def delete_user(user_id):
    """
    Delete a user by ID
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        bool: True if deleted, False if not found
    """
    if user_id in users_db:
        del users_db[user_id]
        return True
    return False

def get_all_users():
    """
    Retrieve all users
    
    Returns:
        list: List of all users
    """
    return list(users_db.values())

