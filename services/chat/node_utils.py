from services.chat.api_requests import *

def chat_orderID_request(arg, childs_tools, trase=True):
    """
    Request user for the order_id
    """
    return childs_tools[0]["function"]["name"], arg["system_message"], {}

def chat_2steps_request(arg, childs_tools, trase=True):
    """
    Send 2-step code and retrieve order status.
    """
    send_2_step_code(arg["order_id"])
    return childs_tools[0]["function"]["name"], arg["system_message"], get_order_details(arg["order_id"])

def chat_check_2steps(arg, childs_tools, trase=True):
    """
    Process 2-step code and retrieve order status.
    """
    if check_2_step_code(order_id=arg["order_id"],code=arg["2-step_code"]):
        return childs_tools[0]["function"]["name"], "Verification was successful. " + arg["system_message"], get_order_details(arg["order_id"])
    return "", "There was a problem with verification, contact the call center or try it again latter", get_order_details(arg["order_id"])

def canceling_order(arg, childs_tools, trase=True): ## Output Node
    """
    Process Order cancelation and retrieve order status.
    """
    final_status = cancel_order(order_id=arg["order_id"],reason=arg["motivations"]).status
    if final_status == "cancelled":
        return "", arg["system_message"]
    elif final_status in ["shipped", "delivered"]:
        return "", f"The order can't be cancelled because it's {final_status}"
    else:
        return "", "There was a problem, contact the call center or try it again latter"
    
def returning_to_root(arg, childs_tools, trase=True): ## Output Node
    """
    User regret order cancelation, returning to root node 
    """
    return "", arg["system_message"]


def order_status_check(arg, childs_tools, trase=True):
    """
    Retrieve the current status of the order from tracking database.
    """
    
    return childs_tools[0]["function"]["name"], track_order(arg["order_id"])

def update_notification_preferences(arg, childs_tools, trase=True): ## Output Node
    """
    Update a customer's notification preferences for order tracking.
    """
    # Implementation would update customer preferences in database
    return "", arg["system_message"]

def chat_tracking_info(arg, childs_tools, trase=True):
    """
    Process user messages related to order tracking for additional information requests.
    """
    # Implementation would analyze the message and return appropriate tracking details
    return childs_tools[0]["function"]["name"], arg["system_message"], get_order_details(arg["order_id"])

def chat_flexible_handler(arg, childs_tools, trase=True):
    """
    Handles flexible conversation scenarios including:
    1. Normal conversation continuation
    2. Error recovery from other pipelines
    3. Special request handling
    4. System reset when needed
    """
    user_message = arg.get("user_message", "")
    system_message = arg.get("system_message", "")
    route_info = arg.get("route_info", "default")
    
    # Error detection keywords
    error_indicators = ["cannot process", "error", "failed", "unable to complete", 
                        "technical difficulty", "system error"]
    
    # Check if coming from error condition
    is_error_recovery = any(indicator in system_message.lower() for indicator in error_indicators)
    
    # Check for special requests or frustration indicators
    special_request_indicators = ["speak to human", "customer service", "representative", 
                                 "this is not working", "frustrated", "annoying"]
    needs_special_handling = any(indicator in user_message.lower() for indicator in special_request_indicators)
    
    # Determine appropriate response
    if is_error_recovery:
        response = {
            "system_message": "I apologize for the difficulty. Let's start over. How can I assist you today?",
            "reset_to_root": True
        }
    elif needs_special_handling:
        response = {
            "system_message": "I understand this may be frustrating. Would you like me to connect you with customer service? In the meantime, I'm happy to try addressing your concerns differently.",
            "reset_to_root": False
        }
    else:
        # Normal conversation flow
        response = {
            "system_message": system_message,
            "reset_to_root": False
        }
    
    return childs_tools[0]["function"]["name"], response["system_message"], response