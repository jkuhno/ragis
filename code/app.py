import os
import gradio as gr

import rag_module as rag
import data_loader as loader
import databases as db
import kql_module as kql


# Main application. Holds the Gradio UI functionality

if not os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    raise gr.Error("Please set your NVIDIA API KEY in 'Environment ->  Secrets -> Add -> Name=NVIDIA_API_KEY, value=<your-api-key>'")


def input_query_azure(id, old_dropdown, timespan):
    inputs = [kql.get_response(id, "Inputs", timespan)]
    inputs = loader.kql_input_alert_tuple(inputs)
    return gr.Dropdown(inputs), inputs


def load_vectorstore(path=""):
    db.clear()
    try:
        db.load_context("import", path)
    except ValueError as error:
        raise gr.Error(error)


def default_query_azure(id, query):
    responses = []
    for i in query:
        response = kql.get_response(id, i, 30)
        responses.append(response)
    docs_csvs = loader.kql_response_as_csv(responses, query)

    if "Users" in query:
        
    
    # initiate the vector database
    load_vectorstore(docs_csvs)
    return docs_csvs


def initiate_input(input_):
    x = loader.get_input_as_pd(input_)
    return x, input_
    

############################### AZURE CONNECTION INTERFACE ###############################
##########################################################################################
with gr.Blocks() as azure:
    input = gr.State()
    
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
                search_alerts = gr.Button("Search alerts")
                
            input_dropdown = gr.Dropdown([], label="Queried inputs")
            generate_btn = gr.Button("Generate")
            output = gr.Textbox(label="Output", lines=5)

            with gr.Accordion(label="debug", open=False):
                debug_metadata = gr.Textbox(label="debug rows", lines=5)
                debug_page = gr.Textbox(label="debug pages", lines=5)
            
        with gr.Column(scale=1, variant='compact'):     
            workspace_id = gr.Textbox(label="Your Log Analytics workspace ID", value="1bffa9d3-05ed-4784-8a15-2dc8d257b039")
            default_query_group = gr.CheckboxGroup(choices=["Closed incidents", "Users"], value="Closed incidents", label="Queries", info="Select at least one")
            default_query_btn = gr.Button("Query")                  

            with gr.Accordion(label="Data inspector", open=False):
                gr.Markdown("Context documents")
                context_display = gr.Textbox(label="Docs queried", lines=5)
                gr.Markdown("Input alerts")
                input_display = gr.Dataframe(label="Input alert")
                

    # Event listeners
    search_alerts.click(fn=input_query_azure, inputs=[workspace_id, input_dropdown, query_time], outputs=[input_dropdown, debug_metadata])
    
    default_query_btn.click(fn=default_query_azure, inputs=[workspace_id, default_query_group], outputs=[context_display])
    
    input_dropdown.select(fn=initiate_input, inputs=input_dropdown, outputs=[input_display, input])
    
    generate_btn.click(fn=rag.generate, inputs=input, outputs=[output, debug_metadata, debug_page])


############################### CSV IMPORT INTERFACE #####################################
##########################################################################################
with gr.Blocks() as csvs:
    input = gr.State()

    gr.Markdown(
        """
        # RAGIS
        Start by populating the backend with company documents.
        After that, select an alert to analyze below.
        """)
    
    with gr.Row():
        with gr.Column(scale=2, variant='panel'):
            input_import = gr.File(label="Import your input csv")    
            generate_btn = gr.Button("Generate")
            output = gr.Textbox(label="Output", lines=5)
            
            with gr.Accordion(label="debug", open=False):
                debug_metadata = gr.Textbox(label="debug rows", lines=5)
                debug_page = gr.Textbox(label="debug pages", lines=5)
            
        with gr.Column(scale=1, variant='compact'):
            document_import = gr.File(label="Import your context csv files", file_count="multiple")
            document_upload_btn = gr.Button("Initiate vetor database with documents")

            with gr.Accordion(label="Data inspector", open=False):
                gr.Markdown("Input alerts")
                input_display = gr.Dataframe(label="Input alert")   

    
    # Event listeners
    document_upload_btn.click(fn=load_vectorstore, inputs=[document_import], outputs=[])

    input_import.change(fn=initiate_input, inputs=input_import, outputs=[input_display, input])

    generate_btn.click(fn=rag.generate, inputs=input, outputs=[output, debug_metadata, debug_page])
                

# Put the UI in a tabbed interface, representing two usage scenarios
app = gr.TabbedInterface(interface_list=[azure, csvs], tab_names=["Azure connection", "Import csv"], theme="base")

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)