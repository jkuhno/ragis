import gradio as gr
import os

def greet(name, intensity):
    return "Hi, " + name + "!" * int(intensity)

input = gr.Textbox(label='Input')
output = gr.Textbox(label='Output', lines=3)

app = gr.Interface(
    fn=greet,
    inputs=[input],
    outputs=[output],
)

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)
