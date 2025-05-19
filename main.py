from demo_front_page.demo_gradio import Chat_Bot_ToT_Interface

app = Chat_Bot_ToT_Interface().create_interface()
app.launch(server_name="0.0.0.0", server_port=7860) # Made it run on all addresses



