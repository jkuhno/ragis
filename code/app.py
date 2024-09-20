import gradio as gr
import os

import rag_module as rag
import data_loader as loader
import databases as db

with gr.Blocks() as app:
    with gr.Row():
        with gr.Column(scale=2):
            input_display = gr.Dataframe(label="Input placeholder")
            output = gr.Textbox(label="Output", lines=5)
            btn = gr.Button("Generate")
        with gr.Column(scale=1):
            # Tab for hardcoded dummy inputs for testing without data imports
            with gr.Tab("Dummy inputs"):
                users = gr.Dataframe(label="Sample Entra ID user information", value=loader.get_dummy_users("DataFrame"), interactive=False, type="array")
                context = gr.Dataframe(label="Sample resolved incidents", value=loader.get_dummy_context("DataFrame"), interactive=False, type="array")
                with gr.Row():
                    initiate_vdb_btn = gr.Button("Initiate vector database")
                    clear_vdb_btn = gr.Button(value="Cleared", interactive=False)
                input = gr.Radio(choices=loader.dummy_incident_list, label="Choose input incident")
                initiate_input_btn = gr.Button("Initiate input incident")
            with gr.Tab("Import csv"):
                with gr.Row():
                    image_input = gr.Image()
                    image_output = gr.Image()


    def load_vectorstore():
        db.load_users_vectorstore()
        db.load_context_vectorstore()
        return {
            initiate_vdb_btn: gr.update(value="Vector database loaded", interactive=False),
            clear_vdb_btn: gr.update(value="Clear", interactive=True)
        }
    def clear_vectorstore():
        db.clear()
        return {
            initiate_vdb_btn: gr.update(value="Initiate vector database", interactive=True),
            clear_vdb_btn: gr.update(value="Cleared", interactive=False)
        }

    
    initiate_input_btn.click(fn=loader.get_input_as_pd, inputs=input, outputs=input_display)
    btn.click(fn=rag.generate, inputs=input, outputs=output)
    initiate_vdb_btn.click(fn=load_vectorstore, inputs=[], outputs=[initiate_vdb_btn, clear_vdb_btn])
    clear_vdb_btn.click(fn=clear_vectorstore, inputs=[], outputs=[initiate_vdb_btn, clear_vdb_btn])

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)
