import gradio as gr
from src.agents import run_civic_agent

def chat_interface(message, history):
    response = run_civic_agent(message)
    return str(response)

#Creating the UI.
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Civic-Helper Agent")
    gr.Markdown("Describe a community issue (e.g., 'There is a pothole on Main St').")
    
    chat = gr.ChatInterface(fn=chat_interface)

if __name__ == "__main__":
    print("Starting Civic-Helper...")
    demo.launch()