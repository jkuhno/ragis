import os
import gradio as gr

import rag_module as rag
import data_loader as loader
import databases as db
import kql_module as kql


# Main application. Holds the Gradio UI functionality

if not os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    raise gr.Error("Please set your NVIDIA API KEY in 'Environment ->  Secrets -> Add -> Name=NVIDIA_API_KEY, value=<your-api-key>'")

with gr.Blocks() as azure:
    
    input = gr.State()
    azure_context_path = gr.State()

    gr.Markdown(
        """
        # RAGIS
        Start by populating the backend with company documents.
        After that, select an alert to analyze below.
        """)
    
    with gr.Row():
        
        with gr.Column(scale=2, variant='panel'):
            with gr.Row():
                query_time = gr.Slider(1, 30, value=4, step=1, label="Alert query timespan", info="(in days)")
                initiate_input_btn3 = gr.Button("Search alerts")
            input_dropdown = gr.Dropdown([], label="Queried inputs")
            
            #input_display = gr.Dataframe(label="Input inspector")
            
            generate_btn = gr.Button("Generate")
            output = gr.Textbox(label="Output", lines=5)
            
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
                
            # Tab for querying data from Azure
            with gr.Tab("Azure connection"):
                workspace_id = gr.Textbox(label="Your Log Analytics workspace ID", value="1bffa9d3-05ed-4784-8a15-2dc8d257b039")
                # query_time = gr.Slider(1, 30, value=4, step=1, label="Query timespan", info="(in days)")
                default_query_group = gr.CheckboxGroup(choices=["Closed incidents", "Users"], value="Closed incidents", label="Queries", info="Select at least one")
                default_query_btn = gr.Button("Use a default query")

                # Closed out initially, preferred to use default query
                with gr.Accordion(label="Use a custom query", open=False):
                    """
                    gr.Markdown("Used for custom KQL queries. Use the first box to query context, and the second to query alerts you want to summarize. WARNING! Must include 'AlertName' and 'DisplayName' fields in input alert query.")
                    custom_context = gr.Textbox(label="Context documents", value=kql.KQL_QUERY_CLOSED)
                    custom_alert = gr.Textbox(label="Alerts for analysis", value=kql.KQL_QUERY_ALERTS)
                    custom_query_btn = gr.Button(value="Query")
                    """
                    gr.Markdown("Display query results")
                    response_box = gr.Textbox(label="Docs queried", lines=5)
                    """
                    with gr.Row():
                        kql_upload_btn = gr.Button("Initiate vetor database with Azure docs")
                        clear_vdb_btn3 = gr.Button(value="Cleared", interactive=False)
                    """
                    gr.Markdown("Input alerts")
                    input_display = gr.Dataframe(label="Input inspector")
                    #input_dropdown = gr.Dropdown([], label="Queried inputs")
                    #initiate_input_btn3 = gr.Button("Initiate input incident")
                  
    
    # tab = "dummy" or import"
    def load_vectorstore(tab, path=""):
        db.clear()
        try:
            if tab == "Initiate vector database":
                db.load_context("dummy")
            elif tab == "Initiate vetor database with documents" or "Initiate vetor database with Azure docs":
                db.load_context("import", path)
        except ValueError as error:
            raise gr.Error(error)

        
        return {
            initiate_vdb_btn: gr.update(value="Vector database loaded", interactive=False),
            document_upload_btn: gr.update(value="Vector database loaded", interactive=False),
            kql_upload_btn: gr.update(value="Vector database loaded", interactive=False),
            clear_vdb_btn1: gr.update(value="Clear", interactive=True),
            clear_vdb_btn2: gr.update(value="Clear", interactive=True),
            clear_vdb_btn3: gr.update(value="Clear", interactive=True)
        }


    def clear_vectorstore():
        db.clear()
        return {
            initiate_vdb_btn: gr.update(value="Initiate vector database", interactive=True),
            document_upload_btn: gr.update(value="Initiate vetor database with documents", interactive=True),
            kql_upload_btn: gr.update(value="Initiate vetor database with Azure docs", interactive=True),
            clear_vdb_btn1: gr.update(value="Cleared", interactive=False),
            clear_vdb_btn2: gr.update(value="Cleared", interactive=False),
            clear_vdb_btn3: gr.update(value="Cleared", interactive=False)
        }
        

    def initiate_input(input_):
        x = loader.get_input_as_pd(input_)
        return x, input_

    
    # id: Log Analytis workspace id
    # query: default queries made from the UI, what user checks from ["Closed incidents", "Users"]
    # old_dropdown: Populating the dropdown component requires the component to be passed as argument to the function. Gradio things.
    # timespan: Timespan for the query
    #
    #TODO: remove the need for passing lists around
    def default_query_azure(id, query, old_dropdown, timespan):
        # Context documents
        responses = []
        for i in query:
            response = kql.get_response(id, i, timespan)
            responses.append(response)
        docs_csvs = loader.kql_response_as_csv(responses, query)

        # Input alerts
        inputs = [kql.get_response(id, "Inputs", timespan)]
        inputs = loader.kql_input_alert_tuple(inputs)
        
        return docs_csvs, gr.Dropdown(inputs), docs_csvs

    """
    def custom_query_azure(id, context_query, input_query, old_dropdown, timespan):
        # Context documents
        context = [kql.get_response(id, context_query, timespan)]
        docs_csvs = loader.kql_response_as_csv(context, "custom")

        # Input alerts
        inputs = [kql.get_response(id, input_query, timespan)]
        inputs = loader.kql_input_alert_tuple(inputs)
        
        return docs_csvs, gr.Dropdown(inputs), docs_csvs
    """
    """
    # Dummy data
    initiate_vdb_btn.click(fn=load_vectorstore, inputs=initiate_vdb_btn, outputs=[initiate_vdb_btn, document_upload_btn, kql_upload_btn, clear_vdb_btn1, clear_vdb_btn2, clear_vdb_btn3])
    clear_vdb_btn1.click(fn=clear_vectorstore, inputs=[], outputs=[initiate_vdb_btn, document_upload_btn, kql_upload_btn, clear_vdb_btn1, clear_vdb_btn2, clear_vdb_btn3])

    initiate_input_btn1.click(fn=initiate_input, inputs=input_dummy, outputs=[input_display, input])

    
    # Import csv
    document_upload_btn.click(fn=load_vectorstore, inputs=[document_upload_btn, document_import], outputs=[initiate_vdb_btn, document_upload_btn, kql_upload_btn, clear_vdb_btn1, clear_vdb_btn2, clear_vdb_btn3])
    clear_vdb_btn2.click(fn=clear_vectorstore, inputs=[], outputs=[initiate_vdb_btn, document_upload_btn, kql_upload_btn, clear_vdb_btn1, clear_vdb_btn2, clear_vdb_btn3])

    initiate_input_btn2.click(fn=initiate_input, inputs=input_import, outputs=[input_display, input])

    
    # Azure integration
    default_query_btn.click(fn=default_query_azure, inputs=[workspace_id, default_query_group, input_dropdown, query_time], outputs=[response_box, input_dropdown, azure_context_path])
    
    kql_upload_btn.click(fn=load_vectorstore, inputs=[kql_upload_btn, azure_context_path], outputs=[initiate_vdb_btn, document_upload_btn, kql_upload_btn, clear_vdb_btn1, clear_vdb_btn2, clear_vdb_btn3])
    clear_vdb_btn3.click(fn=clear_vectorstore, inputs=[], outputs=[initiate_vdb_btn, document_upload_btn, kql_upload_btn, clear_vdb_btn1, clear_vdb_btn2, clear_vdb_btn3])

    initiate_input_btn3.click(fn=initiate_input, inputs=input_dropdown, outputs=[input_display, input])

    custom_query_btn.click(fn=custom_query_azure, inputs=[workspace_id, custom_context, custom_alert, input_dropdown, query_time], outputs=[response_box, input_dropdown, azure_context_path])

    
    # Generate summary
    generate_btn.click(fn=rag.generate, inputs=input, outputs=[output, debug_metadata, debug_page])
    """

with gr.Blocks() as csvs:
    output = gr.Textbox(label="Output", lines=5)

app = gr.TabbedInterface([demo, csvs], ["Azure connection", "Import csv"])

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)