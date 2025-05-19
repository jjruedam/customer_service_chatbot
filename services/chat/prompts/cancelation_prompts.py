### cancel_node
cancel_parameters = {"user_message": {
                      "type": "string",
                      "description": "message sent by the user"
                    }}
cancel_node_template = """Analyze if the user is requesting to cancel an order and determine if they've provided an Order ID.
                     
Order cancellation policy:
- Orders can be cancelled within 2 hours of placement with no penalty
- Orders that have not yet entered processing can be cancelled through the customer portal
- Orders in processing can be cancelled with a 5% cancellation fee if components have been reserved
- Orders that have been shipped cannot be cancelled but may be eligible for return

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

### sending_verification_node
sending_verification_parameters = {"order_id": {
                          "type": "integer",
                          "description": "Order identification numeric code"
                        },
                          "system_message": {
                          "type": "string",
                          "description": "chat bot message to request for the 2-step code sent to order associated email address"
                        }}

### preprocesing_code_node
preprocesing_code_parameters = {"user_message": {
                                  "type": "string",
                                  "description": "message sent by the user"
                                }}

preprocesing_code_node_template = """Analyze if the user has provided the 6-digit two-step verification code sent to their email.
                     
If the code is provided:
1. Extract the 6-digit verification code
2. Confirm we have both the Order ID and verification code to proceed with cancellation
3. Confirme the reason why user wants to cancel the order
4. Check if the user really wants to cancel the order listing items
5. Proceed with the cancelation

If the code is not provided or is invalid (not 6 digits), kindly ask the user to check their email and provide the complete 6-digit code.

User message: {user_message}"""

### check_verification_node
check_verification_parameters = {"order_id": {
                            "type": "integer",
                            "description": "Order identification numeric code"
                        },
                          "2-step_code": {
                            "type": "integer",
                            "description": "6 digit long integer"
                        },
                          "system_message": {
                            "type": "string",
                            "description": "chat bot message for reason collection or confirmation"
                        }}



### preprocessing_motivations_node
preprocessing_motivations_parameters = {"user_message": {
                                          "type": "string",
                                          "description": "message sent by the user"
                                        }}

preprocessing_motivations_node_template= """Analyze if the user has:
1. Confirmed ones that they want to proceed with the cancellation
2. Provided a reason for their cancellation request

Extract and summarize the cancellation reason given. If no reason is provided, politely request one as it's required to complete the cancellation process.

User message: {user_message}"""

### finilizing_cancelation_node
finilizing_cancelation_parameters = {"order_id": {
                          "type": "integer",
                          "description": "Order identification numeric code"
                        },
                          "motivations":{
                          "type": "string",
                          "description": "summary of explicit user's motivations for cancellation" 
                        },
                          "system_message": {
                            "type": "string",
                            "description": "chat bot message confirming cancellation with relevant policy details"
                        }}

