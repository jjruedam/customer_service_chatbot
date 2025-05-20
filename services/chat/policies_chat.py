from services.RAG_support.RAG_processor import RAG
from services.chat.chat_ToT import LLM_Node, Code_Node, ChatToT
from services.chat.node_utils import *
from services.chat.prompts.cancelation_prompts import *
from services.chat.prompts.tracking_prompts import *
policy_rag = RAG(f"services\\RAG_support\\pdf_files\\TechStream Computing Web Store Policies.pdf")
shop_rag = RAG(f"services\\RAG_support\\pdf_files\\TechStream Computing Web Store.pdf")

###--- Root ---### Node configuration example
root_parameters = {"user_message": {
                      "type": "string",
                      "description": "message sent by the user"
                    }}

returning_to_root_parameters = {"order_id": {
                            "type": "integer",
                            "description": "Order identification numeric code"
                          },
                            "system_message": {
                              "type": "string",
                              "description": "chat bot message confirming cancellation is not processed"
                          }}

root = LLM_Node(name="root", 
                     description="Entry point to determine user intent", 
                     parameters=root_parameters,
                     template= "Determine which support pipeline best matches the user's request. User message: {user_message}", 
                     model = "gpt-4.1")
Chat_Bot_ToT = ChatToT(root)


### Default Pipelines ###

###--- Node ---###
default_parameters = {"user_message": {
                        "type": "string",
                        "description": "message sent by the user"
                      }}

default_node = LLM_Node(name="default_node", 
                     description="Conversation guide for unclear requests or off-topic queries", 
                     parameters=default_parameters,
                     template= """Handle this user request by determining the appropriate action:

USER MESSAGE: "{user_message}"

GUIDELINES:
1. COMPANY FOCUS: Our chat exists to assist with product information, order management, returns, cancellations, and company policies.

2. DETERMINE REQUEST TYPE:
   - If about products/orders → Suggest shopping_chatting node
   - If about policies → Suggest policies_questions node
   - If about order cancellation → Suggest Cancell_Order node
   - If genuinely unclear → Ask clarifying questions about their needs related to our services

3. OFF-TOPIC HANDLING:
   - For completely unrelated topics, politely redirect to our purpose
   - After 2+ attempts, suggest alternative contact methods:
     * Customer Service: 1-800-555-1234
     * Email: support@techstream.com
     * Store Locator: www.techstream.com/stores

4. RESPONSE STRUCTURE:
   - Be friendly but focused
   - Keep responses under 100 words
   - Provide 1-2 concrete examples of how we can help
   - For repeat unclear requests, gradually introduce alternative contact methods

Your goal is to guide the conversation toward productive company-related topics without appearing dismissive.
""",
                     model = "gpt-4.1")
Chat_Bot_ToT.conect_node_to_node(from_name="root", to_Node=default_node)

###--- Node ---###
shopping_chatting_node = LLM_Node(name="shopping_chatting", 
                     description="Product and shopping information specialist", 
                     parameters=default_parameters,
                     template= """Respond to the user's product or shopping-related query using retrieved product information. Provide specific details about:

If the user seems frustrated or their request cannot be properly addressed with product information alone, route them to the just_chatting node.

You can't process sales, if user express interest on buying a product  induce they to visit web, shop or call.

User message: {user_message}""",
                     model = "gpt-4.1",
                     retriver=shop_rag.get_retriver(request_type="similarity",top_k=4, score_threshold=0.6))
Chat_Bot_ToT.conect_node_to_node(from_name="root", to_Node=shopping_chatting_node)

###--- Node ---###
policies_questions_node = LLM_Node(name="policies_questions", 
                     description="Company policy and customer service information specialist", 
                     parameters=default_parameters,
                     template= """Respond to the user's query about company policies using retrieved policy information. Address questions regarding:

Provide clear, accurate information based on official company policies. If the policy information is ambiguous or the user request falls outside standard policies, indicate this.

If the user seems frustrated, confused, or their request requires special handling beyond standard policy responses, advice him to contact the call center and/or visit the store.

User message: {user_message}""",
                     model = "gpt-4.1",
                     retriver=policy_rag.get_retriver(request_type="similarity",top_k=3, score_threshold=0.6))
Chat_Bot_ToT.conect_node_to_node(from_name="root", to_Node=policies_questions_node)

###--- Node ---###
just_chatting_parameters = {"user_message": {
                          "type": "string",
                          "description": "message sent by the user"
                        },
                          "system_message": {
                          "type": "string",
                          "description": "chat bot message or error handling response"
                        }} 

just_chatting_node = Code_Node(name="just_chatting",
                              description="Flexible conversation handler",
                              parameters=just_chatting_parameters,
                              function=just_chatting_handler,
                              is_interactive=True)

Chat_Bot_ToT.conect_node_to_node(from_name="default_node", to_Node=just_chatting_node)
Chat_Bot_ToT.conect_node_to_node(from_name="shopping_chatting", to_Node=just_chatting_node)
Chat_Bot_ToT.conect_node_to_node(from_name="policies_questions", to_Node=just_chatting_node)

Chat_Bot_ToT.conect_node_to_node(from_name="just_chatting", to_Node=root)

###--- Node ---###
backup_parameters = {
    "user_message": {
        "type": "string",
        "description": "The most recent message sent by the user"
    },
    "route_info": {
        "type": "string",
        "description": "Information about which pipeline routed to this node, including error details or special handling requirements"
    },
    "error_type": {
        "type": "string",
        "description": "Classification of error or special request type if identified",
        "default": "unspecified"
    }
}

backup_node = LLM_Node(name="backup_system", 
                     description="Emergency response system for handling exceptions, errors, and special user situations", 
                     parameters=backup_parameters,
                     template= """You are an advanced exception handling specialist focused on resolving user issues when normal conversation flows break down. Your purpose is to:

1. Diagnose the issue based on route information and conversation history
2. Provide a helpful, empathetic response that addresses the user's immediate concerns
3. Route the conversation appropriately - either back to a functional pipeline or to human assistance when necessary

CURRENT SITUATION:
- User message: "{user_message}"
- Pipeline information: {route_info}
- Error type (if identified): {error_type}

RESPONSE GUIDELINES:
- If the user is expressing frustration: Acknowledge their feelings, apologize sincerely, and offer a clear path forward
- If a technical error occurred: Explain briefly what went wrong without technical jargon and suggest an alternative approach
- If the user requests human assistance: Confirm this request and explain the next steps to connect with customer service
- If the user is stuck in a loop: Help them break out by suggesting a different approach or topic
- If the user wants to cancel or undo a process: Provide clear instructions on how to do so

Always maintain a helpful, professional tone while acknowledging any difficulties the user has experienced. Prioritize solving their immediate problem rather than defending system limitations.

IMPORTANT: Include a recommendation for how the system should proceed (return to main conversation, escalate to human support, or attempt a specific pipeline again).
""",
                     model = "gpt-4.1",
                     retriver=policy_rag.get_retriver(request_type="mmr", top_k=2,lambda_mult=0.5))
Chat_Bot_ToT.conect_node_to_node(from_name="root", to_Node=backup_node)
Chat_Bot_ToT.conect_node_to_node(from_name="backup_system", to_Node=just_chatting_node)

### Cancel Order Pipeline ###

###--- Node ---###
cancel_node = LLM_Node(name="Cancell_Order", 
                     description="Order cancellation intent detection", 
                     parameters=cancel_parameters,
                     template= cancel_node_template,
                     model = "gpt-4.1")
Chat_Bot_ToT.conect_node_to_node(from_name="root", to_Node=cancel_node)

###--- Node ---###
orderID_node = Code_Node(name="orderID_request",
                              description="Interactive function to collect Order ID when not provided",
                              parameters=orderID_parameters,
                              function=chat_orderID_request,
                              is_interactive=True)
Chat_Bot_ToT.conect_node_to_node(from_name="Cancell_Order", to_Node=orderID_node)
Chat_Bot_ToT.conect_node_to_node(from_name="orderID_request", to_Node=cancel_node)

###--- Node ---###
sending_verification_node = Code_Node(name="sending_verification_code",
                              description="Send the 2-step verification code to the email address associated with the Order ID",
                              parameters=sending_verification_parameters,
                              function=chat_2steps_request,
                              is_interactive=True)
Chat_Bot_ToT.conect_node_to_node(from_name="Cancell_Order", to_Node=sending_verification_node)

###--- Node ---###
preprocesing_code_node = LLM_Node(name="preprocesing_code", 
                     description="Extract and validate verification code", 
                     parameters=preprocesing_code_parameters,
                     template=preprocesing_code_node_template,
                     model = "gpt-4.1")
Chat_Bot_ToT.conect_node_to_node(from_name="sending_verification_code", to_Node=preprocesing_code_node)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocesing_code", to_Node=backup_node)

###--- Node ---###
check_verification_node = Code_Node(name="check_cancelation_request",
                              description="Verify order status and eligibility for cancellation based on company policy",
                              parameters=check_verification_parameters,
                              function=chat_check_2steps,
                              is_interactive=True)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocesing_code", to_Node=check_verification_node)

###--- Node ---###
preprocessing_motivations_node = LLM_Node(name="preprocessing_motivations", 
                     description="Process customer's cancellation reason", 
                     parameters=preprocessing_motivations_parameters,
                     template= preprocessing_motivations_node_template,
                     model = "gpt-4.1",
                     retriver=policy_rag.get_retriver(request_type="mmr", filter_key="Cancelation process",top_k=2, lambda_mult=0.8))
Chat_Bot_ToT.conect_node_to_node(from_name="check_cancelation_request", to_Node=preprocessing_motivations_node)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocessing_motivations", to_Node=check_verification_node)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocessing_motivations", to_Node=backup_node)

###--- Node ---### ## Output Node
finilizing_cancelation_node = Code_Node(name="finilizing_cancelation",
                              description="Complete the cancellation process and provide refund information",
                              parameters=finilizing_cancelation_parameters,
                              function=canceling_order)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocessing_motivations", to_Node=finilizing_cancelation_node)

###--- Node ---### ## Output Node
regret_cancelation_node = Code_Node(name="regret_cancelation",
                              description="User regret cancelelation intent detection",
                              parameters=returning_to_root_parameters,
                              function=returning_to_root)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocessing_motivations", to_Node=regret_cancelation_node)
Chat_Bot_ToT.conect_node_to_node(from_name="preprocesing_code", to_Node=regret_cancelation_node)

Chat_Bot_ToT.conect_node_to_node(from_name="regret_cancelation", to_Node=root)

### Order Tracking Pipeline ###

###--- Node ---###
tracking_node = LLM_Node(name="Track_Order", 
                     description="Order tracking intent detection", 
                     parameters=tracking_parameters,
                     template=tracking_node_template,
                     model = "gpt-4.1")
Chat_Bot_ToT.conect_node_to_node(from_name="root", to_Node=tracking_node)

###--- Node ---###
orderID_node2 = Code_Node(name="orderID_request2",
                              description="Interactive function to collect Order ID when not provided",
                              parameters=orderID_parameters,
                              function=chat_orderID_request,
                              is_interactive=True)
Chat_Bot_ToT.conect_node_to_node(from_name="Track_Order", to_Node=orderID_node2)
Chat_Bot_ToT.conect_node_to_node(from_name="orderID_request2", to_Node=tracking_node)

###--- Node ---### 
status_check_node = Code_Node(name="status_check",
                              description="Retrieve the current status of the order from tracking database",
                              parameters=status_check_parameters,
                              function=order_status_check)
Chat_Bot_ToT.conect_node_to_node(from_name="Track_Order", to_Node=status_check_node)

###--- Node ---###
status_processing_node = LLM_Node(name="status_processing", 
                     description="Explain the order status and next steps to the customer", 
                     parameters=status_processing_parameters,
                     template=status_processing_template,
                     model = "gpt-4.1")
Chat_Bot_ToT.conect_node_to_node(from_name="status_check", to_Node=status_processing_node)
Chat_Bot_ToT.conect_node_to_node(from_name="status_processing", to_Node=backup_node)

###--- Node ---###
status_explanation_node = Code_Node(name="status_explanation",
                              description="Retrieve the current status of the order from tracking database",
                              parameters=status_explanation_parameters,
                              function=chat_tracking_info,
                              is_interactive=True)
Chat_Bot_ToT.conect_node_to_node(from_name="status_processing", to_Node=status_explanation_node)

###--- Node ---###
notification_preference_node = LLM_Node(name="notification_preference", 
                     description="Process user's notification preferences request", 
                     parameters=notification_preference_parameters,
                     template=notification_preference_template,
                     model = "gpt-4.1",
                     retriver=policy_rag.get_retriver(request_type="mmr", filter_key="Tracking",top_k=2, lambda_mult=0.8))
Chat_Bot_ToT.conect_node_to_node(from_name="status_explanation", to_Node=notification_preference_node)
Chat_Bot_ToT.conect_node_to_node(from_name="notification_preference", to_Node=backup_node)

###--- Node ---### ## Output Node
update_notifications_node = Code_Node(name="update_notifications",
                              description="Update notification intent detection",
                              parameters=update_notifications_parameters,
                              function=update_notification_preferences,
                              required=["system_message", "order_id"])
Chat_Bot_ToT.conect_node_to_node(from_name="notification_preference", to_Node=update_notifications_node)

###--- Node ---### ## Output Node
no_update_notifications_node = Code_Node(name="tracking_finilizing",
                              description="Finilizing tracking order",
                              parameters=returning_to_root_parameters,
                              function=returning_to_root)
Chat_Bot_ToT.conect_node_to_node(from_name="notification_preference", to_Node=no_update_notifications_node)


fig = Chat_Bot_ToT.visualize_graph(title='Policies Chat Graph')
fig.savefig('my_graph.png', dpi=300)