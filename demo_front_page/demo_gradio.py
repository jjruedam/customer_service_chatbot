import gradio as gr
from services.chat.policies_chat import Chat_Bot_ToT

class Chat_Bot_ToT_Interface():
    def __init__(self):
        self.global_chat_state = gr.State("")
        
    # Mock function to simulate an AI response
    def get_ai_response(self, message, history, image):
        """
        Generates a mock AI response with a typing effect.

        Args:
            message (str): The user's input message.
            history (list): The chat history (list of tuples: (user_msg, ai_msg)).

        Returns:
            str: The AI's response (with a typing effect).
        """

        self.global_chat_state.value, chat_response=Chat_Bot_ToT.run_from(message=message, history=history, image=image,from_node_name=self.global_chat_state.value)

        # Simulate a typing delay
        yield str(chat_response)

    # Function to create the Gradio interface
    def create_interface(self):
        """
        Creates and returns the Gradio ChatInterface.

        Returns:
            gradio.ChatInterface: The Gradio ChatInterface object.
        """
        # Create the ChatInterface
        chat_interface = gr.ChatInterface(
            fn=self.get_ai_response,
            type="messages",
            chatbot=gr.Chatbot(height=500, type="messages"),  # Increased height for better visibility
            textbox=gr.Textbox(placeholder="Type your message here...", container=True), # Added container=True
            title="Chat with Mock AI",
            description="I can answer your questions about company policies and assist you on existing orders process. (Verification Code: 123654)",
            examples=[
                ["I want to cancel my order!!", None],  # Added None for image in examples
                ["where is my package?", None],
                ["Which are the policies about cancelling an order?", None],
            ],
            flagging_mode="never", # Removed the flagging button
            additional_inputs=[
                gr.Image(label="Upload Image", type="pil",  # Ensure PIL type for image processing
                        image_mode="RGBA") # Added image_mode
            ]
        )
        return chat_interface

if __name__ == "__main__":
    # This block is only executed if the script is run directly (not imported)
    app = Chat_Bot_ToT_Interface.create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860) # Made it run on all addresses
