import os
import gradio as gr

import rag_module as rag
import data_loader as loader
import databases as db
import kql_module as kql
import entra_id
import asyncio
import pandas as pd

import simulatorGenerator

theme = gr.themes.Monochrome().set(
    checkbox_label_background_fill="#69B84D",
    checkbox_label_background_fill_hover="#7CD15D",
    #checkbox_background_color_selected="#69B84D",
    #checkbox_background_color_dark="#69B84D",
    #checkbox_background_color_selected_dark="#69B84D",
)

css = """
.btn {
    background-color: #69B84D;
    color: white;
}

.btn:hover {
    background-color: #7CD15D;
}

checkbox {
    background-color: #69B84D; !important
}
"""


# Main application. Holds the Gradio UI functionality

if not os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    raise gr.Error("Please set your NVIDIA API KEY in 'Environment ->  Secrets -> Add -> Name=NVIDIA_API_KEY, value=<your-api-key>'")


def hide_success(success):
    return gr.Markdown("", visible=False)
    

def input_query_azure(id, old_dropdown, timespan):
    inputs = [kql.get_response(id, "Inputs", timespan)]
    inputs = loader.kql_input_alert_tuple(inputs)
    return gr.Dropdown(inputs, label="Queried inputs", visible=True), inputs


def load_vectorstore(success, path=""):
    db.clear()
    try:
        db.load_context(path)
        return gr.Markdown("Success initiating vector database 👍", visible=True)
    except ValueError as error:
        raise gr.Error(error)


def default_query_azure(id, query, success):
    docs_csvs = []
    if "Closed incidents" in query:
        response = [kql.get_response(id, "Closed incidents", 30)]
        docs_csvs.append(loader.kql_response_as_csv(response, query)[0])

    if "Users" in query:
        docs_csvs.append(asyncio.run(entra_id.get_users("csv")))
    
    # initiate the vector database
    markdown = load_vectorstore(success, docs_csvs)
    return docs_csvs, markdown


def initiate_input(input_):
    x = pd.read_csv(input_)
    return x, input_
    

############################### AZURE CONNECTION INTERFACE ###############################
##########################################################################################
with gr.Blocks() as azure:
    input = gr.State()
    
    gr.Markdown(
        """
        # RAGIS
        Start by populating the backend with company documents.\n
        After that, select an alert to analyze below.
        """)
    
    with gr.Row():
        with gr.Column(scale=2, variant='panel'):
            with gr.Row():
                query_time = gr.Slider(1, 30, value=4, step=1, label="Alert query timespan", info="(in days)")
                search_alerts = gr.Button("Search alerts", elem_classes="btn")
                
            input_dropdown = gr.Dropdown([], visible=False)
            generate_btn = gr.Button("Generate", elem_classes="btn")
            output = gr.Textbox(label="Output", lines=5)

            with gr.Accordion(label="debug", open=False):
                debug_metadata = gr.Textbox(label="debug rows", lines=5)
                debug_page = gr.Textbox(label="debug pages", lines=5)

                template = gr.Textbox(label="Template", value="""
                <|begin_of_text|><|start_header_id|>system<|end_header_id|>
                You are an assistant tasked to reason if an input incident is a true positive or a false positive. True positives are incidents that require more attention from the user, false positives usually mean no harm.
                Use the company documents to logically decide if input incident is malicious or not. Flag malicious as true positive and logically acceptable as false positive.
                The user wants a "true positive" or "false positive" prediction, a short summary of your reasoning and a list of key attributes you used for the reasoning.
                <|eot_id|>
                <|start_header_id|>user<|end_header_id|>
                Here is the input incident: {incident}
                Here are the company documents: {documents}
                <|eot_id|>
                <|start_header_id|>assistant<|end_header_id|>""")
                
                use_aug = gr.Checkbox(label="Use query augmentation")
                search_type = gr.Radio(["similarity", "mmr"], value="mmr", label="Search type", info="MMR: Maximal marginal relevance optimizes for similarity to query AND diversity among selected documents.")
                k = gr.Slider(1, 10, value=4, step=1, label="k", info="Number of documents retrieved")
                gr.Markdown("Use these with mmr")
                lambda_mult = gr.Slider(0, 1, value=0.5, step=0.1, label="lambda_mult", info=" Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum. (Default: 0.5)")
                fetch_k = gr.Slider(1, 50, value=19, step=1, label="fetch_k", info="Amount of documents to pass to MMR algorithm")
                
                simulator_btn = gr.Button("Generate", elem_classes="btn")
            
        with gr.Column(scale=1, variant='compact'):     
            workspace_id = gr.Textbox(label="Your Log Analytics workspace ID", value="1bffa9d3-05ed-4784-8a15-2dc8d257b039")
            default_query_group = gr.CheckboxGroup(choices=["Closed incidents", "Users"], value="Closed incidents", label="Queries", info="Select at least one")
            default_query_btn = gr.Button("Query", elem_classes="btn")  
            success = gr.Markdown("", visible=False)

            with gr.Accordion(label="Data inspector", open=False):
                gr.Markdown("Context documents")
                context_display = gr.Textbox(label="Docs queried", lines=5)
                gr.Markdown("Input alerts")
                input_display = gr.Dataframe(label="Input alert")
                

    # Event listeners
    search_alerts.click(fn=input_query_azure, inputs=[workspace_id, input_dropdown, query_time], outputs=[input_dropdown, debug_metadata])

    default_query_btn.click(fn=hide_success, inputs=[success], outputs=[success])
    default_query_btn.click(fn=default_query_azure, inputs=[workspace_id, default_query_group, success], outputs=[context_display, success])
    
    input_dropdown.select(fn=initiate_input, inputs=input_dropdown, outputs=[input_display, input])
    
    generate_btn.click(fn=rag.generate, inputs=input, outputs=[output, debug_metadata, debug_page])
    simulator_btn.click(fn=simulatorGenerator.generate, inputs=[input, template, search_type, k, lambda_mult, fetch_k, use_aug], outputs=[output, debug_metadata, debug_page])


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
            generate_btn = gr.Button("Generate", elem_classes="btn")
            output = gr.Textbox(label="Output", lines=5)
            
            with gr.Accordion(label="debug", open=False):
                debug_metadata = gr.Textbox(label="debug rows", lines=5)
                debug_page = gr.Textbox(label="debug pages", lines=5)
            
        with gr.Column(scale=1, variant='compact'):
            document_import = gr.File(label="Import your context csv files", file_count="multiple")
            document_upload_btn = gr.Button("Initiate vetor database with documents", elem_classes="btn")
            success = gr.Markdown("", visible=False)

            with gr.Accordion(label="Input data inspector", open=False):
                input_display = gr.Dataframe(label="Input alert")   

    
    # Event listeners
    document_upload_btn.click(fn=hide_success, inputs=[success], outputs=[success])
    document_upload_btn.click(fn=load_vectorstore, inputs=[success, document_import], outputs=[success])

    input_import.change(fn=initiate_input, inputs=input_import, outputs=[input_display, input])

    generate_btn.click(fn=rag.generate, inputs=input, outputs=[output, debug_metadata, debug_page])


##########################################################################################
##########################################################################################


# Put the UI in a tabbed interface, representing two usage scenarios
app = gr.TabbedInterface(interface_list=[azure, csvs], tab_names=["Azure connection", "Import csv"], theme=theme, css=css)

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)