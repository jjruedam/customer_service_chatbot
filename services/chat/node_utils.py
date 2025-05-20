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

def just_chatting_handler(arg, childs_tools, trase=True):
    """
    Handles just chatting loop
    """
    return childs_tools[0]["function"]["name"], arg["system_message"], {}