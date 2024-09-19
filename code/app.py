import gradio as gr
import os

import rag_module as rag
import data_loader as loader

with gr.Blocks() as app:
    with gr.Row():
        input = gr.Radio(loader.dummy_incident_list)
    with gr.Row():
        output = gr.Textbox(label="Output")
    with gr.Row():
        btn = gr.Button("Generate")
        btn.click(fn=rag.generate, inputs=input, outputs=output)


proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)
