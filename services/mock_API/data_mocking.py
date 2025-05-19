from services.mock_API.data_models import OrderGenericDetailsResponse, OrderCancellationRequest, OrderTrackingResponse
import random
from functools import lru_cache
from typing import Dict, List, Any, Optional

# --- Mock Data ---
#  Moved mock data generation into functions, to be used with seed.

# Global storage for generated data
_data_storage = {}


def generate_mock_items(seed: int) -> List[Dict[str, Any]]:
    """
    Generates mock order items, varying by seed.
    Uses a cache to ensure the same seed always produces the same items.
    
    Args:
        seed: An integer seed to generate deterministic results
        
    Returns:
        A list of item dictionaries
    """
    cache_key = f"items_{seed}"
    
    # Return cached data if it exists
    if cache_key in _data_storage:
        return _data_storage[cache_key]
    
    # Generate new data if not in cache
    random.seed(seed)  # Use seed for deterministic results
    num_items = random.randint(1, 5)
    items = [
        {
            "item_id": i + 1,
            "name": f"Product {i + 1}",
            "quantity": random.randint(1, 3),
            "price": round(random.uniform(10, 100), 2),
        }
        for i in range(num_items)
    ]
    
    # Store in cache
    _data_storage[cache_key] = items
    return items


def update_mock_item(seed: int, item_id: int, updates: Dict[str, Any]) -> bool:
    """
    Updates a specific mock item in the cache.
    
    Args:
        seed: The seed used to generate the original items
        item_id: The ID of the item to update
        updates: Dictionary of fields to update
        
    Returns:
        True if successful, False if the item wasn't found
    """
    cache_key = f"items_{seed}"
    
    if cache_key not in _data_storage:
        return False
    
    items = _data_storage[cache_key]
    for item in items:
        if item["item_id"] == item_id:
            item.update(updates)
            return True
    
    return False


def generate_order_details(order_id: int) -> OrderGenericDetailsResponse:
    """
    Generates mock order details based on the order ID and seed.
    Uses a cache to ensure consistent results for the same order_id.
    
    Args:
        order_id: The order ID to generate details for
        
    Returns:
        An OrderGenericDetailsResponse with the order details
    """
    cache_key = f"order_{order_id}"
    
    # Return cached response if it exists
    if cache_key in _data_storage:
        return _data_storage[cache_key]
    
    # Generate new response if not in cache
    random.seed(order_id)  # Use seed to make the response deterministic
    
    items = generate_mock_items(order_id)
    response = OrderGenericDetailsResponse(
        order_id=order_id,
        order_date="2024-07-28",
        customer_name="John Doe",
        items=items,
        total_amount=sum(item["quantity"] * item["price"] for item in items),
        status=random.choice(["pending", "processing", "components gathered", 
                             "quality check", "packaging", "shipped", 
                             "out for delivery", "delivered"]),
        tracking_id=f"TRACK-{order_id}-{random.randint(100, 999)}",
        other_details={"warehouse_location": random.choice(["NY", "LA", "CHI"])},
        cancellation_reason=""
    )
    
    # Store in cache
    _data_storage[cache_key] = response
    return response


def update_order_details(order_id: int, updates: Dict[str, Any]) -> bool:
    """
    Updates specific fields of an order in the cache.
    
    Args:
        order_id: The ID of the order to update
        updates: Dictionary of fields to update
        
    Returns:
        True if successful, False if the order wasn't found
    """
    cache_key = f"order_{order_id}"
    
    if cache_key not in _data_storage:
        return False
    
    order = _data_storage[cache_key]
    
    # Process allowed fields to update
    for key, value in updates.items:
        if hasattr(order, key):
            setattr(order, key, value)
            
            # Recalculate total if items were updated
            if key == "items":
                order.total_amount = sum(item["quantity"] * item["price"] for item in order.items)
    
    return True


def clear_mock_data_cache() -> None:
    """
    Clears all cached mock data.
    Useful for testing or resetting the state.
    """
    global _data_storage
    _data_storage = {}
    