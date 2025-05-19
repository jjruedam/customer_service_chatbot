import requests
import json

# 1. Get Order Details
def get_order_details(order_id: int, include_tracking: bool = False):
    """
    Retrieves order details using the /order/details endpoint.

    Args:
        order_id: The ID of the order to retrieve.
        include_tracking: Whether to include tracking information.

    Returns:
        The JSON response from the API.
    """
    url = f"http://127.0.0.1:8000/order/details?order_id={order_id}"
    if include_tracking:
        url += "&include_tracking=true"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()



# 2. Cancel Order
def cancel_order(order_id: int, reason: str):
    """
    Cancels an order using the /order/cancel endpoint.

    Args:
        order_id: The ID of the order to cancel.
        reason: The reason for the cancellation.

    Returns:
        The JSON response from the API.
    """
    url = "http://127.0.0.1:8000/order/cancel"
    headers = {"Content-Type": "application/json"}
    payload = {"order_id": order_id, "reason": reason}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()



# 3. Track Order
def track_order(order_id: int):
    """
    Tracks an order using the /order/track endpoint.

    Args:
        order_id: The ID of the order to track.

    Returns:
        The JSON response from the API.
    """
    url = f"http://127.0.0.1:8000/order/track?order_id={order_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()



# 4. Security Process
def send_2_step_code(order_id: int):
    """
    Send verification code to associated email adress.

    Args:
        order_id: The ID of the order to retrieve.

    Returns:
        None 
    """

    url = f"http://127.0.0.1:8000//security/send_2_steps_code"
    payload = {"order_id": 12345}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    

def check_2_step_code(order_id: int, code: int):
    """
    Verify code to associated email adress.

    Args:
        order_id: The ID of the order.
        code: 2-steps verification code.

    Returns:
        bool: code is accepted
    """
    url = f"http://127.0.0.1:8000//security/verify_2_steps_code"
    params ={
       "order_id":order_id,
       "code":code
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()["verified"]
