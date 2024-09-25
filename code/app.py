import os
import gradio as gr

import rag_module as rag
import data_loader as loader
import databases as db
import kql_module as kql



with gr.Blocks() as app:
    if not os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
        raise gr.Error("Please set your NVIDIA API KEY in 'Environment ->  Secrets -> Add -> Name=NVIDIA_API_KEY, value=<your-api-key>'")
    
    input = gr.State()
    #azure_client = gr.State()
    with gr.Row():
        with gr.Column(scale=2):
            input_display = gr.Dataframe(label="Input placeholder")
            output = gr.Textbox(label="Output", lines=5)
            generate_btn = gr.Button("Generate")
            debug_metadata = gr.Textbox(label="debug rows", lines=5)
            debug_page = gr.Textbox(label="debug pages", lines=5)
            
        with gr.Column(scale=1):
            
            # Tab for hardcoded dummy inputs for testing without data imports
            with gr.Tab("Dummy inputs"):
                users = gr.Dataframe(label="Sample Entra ID user information", value=loader.get_dummy_users("DataFrame"), interactive=False, type="array")
                context = gr.Dataframe(label="Sample resolved incidents", value=loader.get_dummy_context("DataFrame"), interactive=False, type="array")
                with gr.Row():
                    initiate_vdb_btn = gr.Button("Initiate vector database")
                    clear_vdb_btn1 = gr.Button(value="Cleared", interactive=False)
                input_dummy = gr.Radio(choices=loader.dummy_incident_list, label="Choose input incident")
                initiate_input_btn1 = gr.Button("Initiate input incident")

            # Tab for importing own csv files
            with gr.Tab("Import csv"):
                with gr.Row():
                    document_import = gr.File(label="Import your context csv files", file_count="multiple")
                with gr.Row():
                    document_upload_btn = gr.Button("Initiate vetor database with documents")
                    clear_vdb_btn2 = gr.Button(value="Cleared", interactive=False)
                input_import = gr.File(label="Import your input csv")
                initiate_input_btn2 = gr.Button("Initiate input incident")
                
            with gr.Tab("Azure connection"):
                workspace_id = gr.Textbox(label="Your Log Analytics workspace ID")
                azure_connection_btn = gr.Button("Query through KQL")
                kql_response = gr.Dataframe(label="KQL query results")
    
    
    # tab = "dummy" or import"
    def load_vectorstore(tab, path=" "):
        db.clear()
        if tab == "Initiate vector database":
            db.load_context("dummy")
        elif tab == "Initiate vetor database with documents":
            db.load_context("import", path)
        
        return {
            initiate_vdb_btn: gr.update(value="Vector database loaded", interactive=False),
            document_upload_btn: gr.update(value="Vector database loaded", interactive=False),
            clear_vdb_btn1: gr.update(value="Clear", interactive=True),
            clear_vdb_btn2: gr.update(value="Clear", interactive=True)
        }

    
    def clear_vectorstore():
        db.clear()
        return {
            initiate_vdb_btn: gr.update(value="Initiate vector database", interactive=True),
            document_upload_btn: gr.update(value="Initiate vetor database with documents", interactive=True),
            clear_vdb_btn1: gr.update(value="Cleared", interactive=False),
            clear_vdb_btn2: gr.update(value="Cleared", interactive=False)
        }
        

    def initiate_input(input_):
        x = loader.get_input_as_pd(input_)
        return x, input_


    def query_azure(id):
        return kql.response_as_df(id)
        
    
    # Dummy data
    initiate_vdb_btn.click(fn=load_vectorstore, inputs=initiate_vdb_btn, outputs=[initiate_vdb_btn, document_upload_btn, clear_vdb_btn1, clear_vdb_btn2])
    clear_vdb_btn1.click(fn=clear_vectorstore, inputs=[], outputs=[initiate_vdb_btn, document_upload_btn, clear_vdb_btn1, clear_vdb_btn2])

    initiate_input_btn1.click(fn=initiate_input, inputs=input_dummy, outputs=[input_display, input])

    # Import csv
    document_upload_btn.click(fn=load_vectorstore, inputs=[document_upload_btn, document_import], outputs=[initiate_vdb_btn, document_upload_btn, clear_vdb_btn1, clear_vdb_btn2])
    clear_vdb_btn2.click(fn=clear_vectorstore, inputs=[], outputs=[initiate_vdb_btn, document_upload_btn, clear_vdb_btn1, clear_vdb_btn2])

    initiate_input_btn2.click(fn=initiate_input, inputs=input_import, outputs=[input_display, input])

    # Azure integration
    azure_connection_btn.click(fn=query_azure, inputs=workspace_id, outputs=kql_response)
    
    # Generate summary
    generate_btn.click(fn=rag.generate, inputs=input, outputs=[output, debug_metadata, debug_page])


proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)