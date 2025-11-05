"""
Item service - handles business logic for item operations
In a real application, this would interact with a database
"""

# Mock database
items_db = {
    1: {'id': 1, 'name': 'Laptop', 'description': 'High-performance laptop'},
    2: {'id': 2, 'name': 'Mouse', 'description': 'Wireless mouse'},
    3: {'id': 3, 'name': 'Keyboard', 'description': 'Mechanical keyboard'},
    4: {'id': 4, 'name': 'Monitor', 'description': '27-inch 4K monitor'},
    5: {'id': 5, 'name': 'Headphones', 'description': 'Noise-cancelling headphones'}
}
next_item_id = 6

def get_item(item_id):
    """
    Retrieve an item by ID
    
    Args:
        item_id: The ID of the item to retrieve
        
    Returns:
        dict: Item data if found, None otherwise
    """
    return items_db.get(item_id)

def get_all_items(limit=10, offset=0):
    """
    Retrieve all items with pagination
    
    Args:
        limit: Maximum number of items to return
        offset: Number of items to skip
        
    Returns:
        list: List of items
    """
    all_items = list(items_db.values())
    return all_items[offset:offset + limit]

def create_item(name, description=''):
    """
    Create a new item
    
    Args:
        name: The item's name
        description: The item's description (optional)
        
    Returns:
        dict: The newly created item
    """
    global next_item_id
    
    item = {
        'id': next_item_id,
        'name': name,
        'description': description
    }
    items_db[next_item_id] = item
    next_item_id += 1
    
    return item

def update_item(item_id, data):
    """
    Update an existing item
    
    Args:
        item_id: The ID of the item to update
        data: Dictionary containing fields to update
        
    Returns:
        dict: Updated item data if found, None otherwise
    """
    if item_id not in items_db:
        return None
    
    item = items_db[item_id]
    
    # Update only provided fields
    if 'name' in data:
        item['name'] = data['name']
    if 'description' in data:
        item['description'] = data['description']
    
    return item

def delete_item(item_id):
    """
    Delete an item by ID
    
    Args:
        item_id: The ID of the item to delete
        
    Returns:
        bool: True if deleted, False if not found
    """
    if item_id in items_db:
        del items_db[item_id]
        return True
    return False

