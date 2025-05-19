### tracking_node
tracking_parameters = {"user_message": {
                      "type": "string",
                      "description": "message sent by the user"
                    }}
tracking_node_template = """Analyze if the user is requesting to track an order and determine if they've provided an Order ID.

Order tracking methods:
- All orders are assigned a unique tracking number ("Order_id")
- Orders can be tracked through customer support, the mobile app, or via tracking links in emails
- Order statuses include: Pending, Order Processing, Components Gathered, Quality Check, Packaging, Shipped, Out for Delivery, and Delivered

If the user has provided an Order ID number, extract and return it. If not, request the Order ID.
User message: {user_message}"""

### orderID_node
orderID_parameters = {"user_message": {
                        "type": "string",
                        "description": "message sent by the user"
                      },
                        "system_message": {
                        "type": "string",
                        "description": "chat bot message to request for the order id"
                      }}

### status_check_node
status_check_parameters = {"order_id": {
                          "type": "integer",
                          "description": "Order identification numeric code"
                        },
                          "system_message": {
                          "type": "string",
                          "description": "chat bot message with current order status information"
                        }}

### status_processing_node
status_processing_parameters = {"order_id": {
                            "type": "integer",
                            "description": "Order identification numeric code"
                        },
                          "status": {
                            "type": "string",
                            "description": "Current status of the order in the tracking pipeline"
                        },
                          "tracking_events": {
                            "type": "string",
                            "description": "Description of order traces"
                        }}

status_processing_template = """Provide a detailed explanation of the order status to the customer based on the tracking information.

Order ID: {order_id}
Current Status: {status}
Tracking Events Traces: {tracking_events}

Explain what the current status means in the context of our order processing pipeline:
- Pending: Order received and payment being verified
- Order Processing: Order confirmed and components being allocated
- Components Gathered: All components for the order have been collected
- Quality Check: Order is undergoing quality assurance
- Packaging: Order is being packaged for shipment
- Shipped: Order has been dispatched from our warehouse
- Out for Delivery: Order is with the local delivery service
- Delivered: Order has been successfully delivered

Provide relevant information based on the current stage and ask if they would like to update their notification preferences for this order."""

### status_explanation_node
status_explanation_parameters={"order_id": {
                          "type": "integer",
                          "description": "Order identification numeric code"
                        },
                          "system_message": {
                          "type": "string",
                          "description": "chat bot message with current order status information and asking if user would like to update their notification preferences"
                        }}

### notification_preference_node
notification_preference_parameters = {"user_message": {
                                  "type": "string",
                                  "description": "message sent by the user"
                                }}

notification_preference_template = """Analyze if the user would like to update their notification preferences for order tracking or finilize the process without updates.

Determine if the user:
1. Wants, or No, to enable/disable any notification methods
2. Has specified which notification methods they prefer
3. Needs more information about notification options

If the user has expressed clear notification preferences, extract and summarize them for processing.
If not, finish the process.

User message: {user_message}"""

### update_notifications_node
update_notifications_parameters = {"order_id": {
                          "type": "integer",
                          "description": "Order identification numeric code"
                        },
                          "email_notifications": {
                          "type": "boolean",
                          "description": "Whether to enable email notifications"
                        },
                          "sms_notifications": {
                          "type": "boolean",
                          "description": "Whether to enable SMS notifications"
                        },
                          "app_notifications": {
                          "type": "boolean",
                          "description": "Whether to enable mobile app notifications"
                        },
                          "phone_number": {
                          "type": "string",
                          "description": "Phone number for SMS notifications, if enabled"
                        },
                          "system_message": {
                            "type": "string",
                            "description": "chat bot message confirming notification preference updates"
                        }}

