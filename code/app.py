import gradio as gr
import os

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

app = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
)

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)