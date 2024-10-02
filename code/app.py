# Copyright (c) 2024 Jani Kuhno, Joel Kataja
# https://www.apache.org/licenses/LICENSE-2.0.txt License.
# Author: Jani Kuhno

# Main application. Holds the Gradio UI functionality

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

# Styling

theme = gr.themes.Monochrome().set(
    checkbox_label_background_fill="#69B84D",
    checkbox_label_background_fill_hover="#7CD15D"
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


if not os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    raise gr.Error("Please set your NVIDIA API KEY in 'Environment ->  Secrets -> Add -> Name=NVIDIA_API_KEY, value=<your-api-key>'")


def hide_success(success):
    return gr.Markdown("", visible=False)
    

def input_query_azure(id, old_dropdown, timespan):
    # Check if "AZURE_CLIENT_ID" is set
    if not os.getenv("AZURE_CLIENT_ID"):
        raise gr.Error("Please set your AZURE CLIENT ID in 'Environment ->  Secrets -> Add -> Name=AZURE_CLIENT_ID, value=<your-application-id>'")
    if not os.getenv("AZURE_CLIENT_ID"):
        raise gr.Error("Please set your AZURE TENANT ID in 'Environment ->  Secrets -> Add -> Name=AZURE_CLIENT_ID, value=<your-tenant-id>'")
    if not os.getenv("AZURE_CLIENT_ID"):
        raise gr.Error("Please set your AZURE CLIENT SECRET in 'Environment ->  Secrets -> Add -> Name=AZURE_CLIENT_ID, value=<your-client-secret>'")
        
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
        # Check if "AZURE_CLIENT_ID" is set
    if not os.getenv("AZURE_CLIENT_ID"):
        raise gr.Error("Please set your AZURE CLIENT ID in 'Environment ->  Secrets -> Add -> Name=AZURE_CLIENT_ID, value=<your-application-id>'")
    if not os.getenv("AZURE_CLIENT_ID"):
        raise gr.Error("Please set your AZURE TENANT ID in 'Environment ->  Secrets -> Add -> Name=AZURE_CLIENT_ID, value=<your-tenant-id>'")
    if not os.getenv("AZURE_CLIENT_ID"):
        raise gr.Error("Please set your AZURE CLIENT SECRET in 'Environment ->  Secrets -> Add -> Name=AZURE_CLIENT_ID, value=<your-client-secret>'")
        
    docs_csvs = []
    if "Users" in query:
        docs_csvs.append(asyncio.run(entra_id.get_users("csv")))
    
    if "Closed incidents" in query:
        response = [kql.get_response(id, "Closed incidents", 30)]
        docs_csvs.append(loader.kql_response_as_csv(response, query)[0])
    
    # initiate the vector database
    markdown = load_vectorstore(success, docs_csvs)
    return docs_csvs, markdown


def initiate_input(input_):
    x = pd.read_csv(input_, index_col=False)
    return x, input_
    

############################### AZURE CONNECTION INTERFACE ###############################
##########################################################################################
with gr.Blocks() as azure:
    
    input = gr.State()
    
    gr.Markdown(
        """
        # RAGIS
        
        **On the right:**  
        Query documents you need from Azure and initiate a vector database.
        
        **On the left:**  
        Search for new incidents during the selected timespan.
        
        After, press **Generate** to get a predictive summary.
        
        > *Note: It is AI-generated and may contain mistakes or incorrect analysis.*
        
        ---
        
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
                debug_metadata = gr.Textbox(label="Context rows", lines=5)
                debug_page = gr.Textbox(label="Context pages", lines=5)

                template = gr.Textbox(label="Template", value="""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an intelligent security assistant tasked with determining if an input incident is a "true positive" or "false positive."

### Definitions:
- **True Positive**: An incident that poses a real threat or indicates malicious activity, requiring immediate attention and action.
- **False Positive**: An incident that is benign and poses no real threat, typically resulting from misclassification or non-malicious behavior.

### Instructions:
1. **Analyze the Incident**: Carefully evaluate the details of the input incident provided below.
2. **Use Company Documents**: Utilize the accompanying company documents to gather context, evaluate threat indicators, and make your determination. Focus on attributes like:
   - User behavior anomalies
   - Known malicious signatures
   - Historical incident data
   - **Job title and role appropriateness**: Check if the job title in the company documents matches the assigned role in the incident. If the job title does not warrant assigning a new privileged role, classify the incident as a "true positive."
3. **Reasoning Process**:
   - Identify and explain any attributes from the documents that indicate whether the incident is malicious or benign.
   - If there are signs of malicious intent (e.g., matching known attack patterns, job title not matching privileged role assignment), classify the incident as a "true positive."
   - If the incident shows benign characteristics (e.g., known safe IPs, normal user behavior), classify it as a "false positive."

### Response Format:
1. **Classification**: Indicate whether the incident is a "true positive" or "false positive."
2. **Reasoning**: Provide a short summary of your reasoning based on evidence from the incident and company documents.
3. **Key Attributes**: List key indicators from the documents that influenced your decision.

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Here is the input incident: {incident}
Here are the company documents: {documents}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>""")
                
                use_aug = gr.Checkbox(label="Use query augmentation")
                search_type = gr.Radio(["similarity", "mmr"], value="mmr", label="Search type", info="MMR: Maximal marginal relevance optimizes for similarity to query AND diversity among selected documents.")
                k = gr.Slider(1, 10, value=5, step=1, label="k", info="Number of documents retrieved")
                gr.Markdown("Use these with mmr")
                lambda_mult = gr.Number(label="lambda_mult", info=" Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum, changes of 0.001 make a difference. (Default: 0.5)")
                fetch_k = gr.Slider(1, 50, value=50, step=1, label="fetch_k", info="Amount of documents to pass to MMR algorithm")
                
                simulator_btn = gr.Button("Generate", elem_classes="btn")
            
        with gr.Column(scale=1, variant='compact'):     
            workspace_id = gr.Textbox(label="Your Log Analytics workspace ID", type="password")
            default_query_group = gr.CheckboxGroup(choices=["Closed incidents", "Users"], value="Closed incidents", label="Queries", info="Select at least one")
            default_query_btn = gr.Button("Query", elem_classes="btn")  
            success = gr.Markdown("", visible=False)

            with gr.Accordion(label="Data inspector", open=False):
                context_display = gr.Textbox(label="Docs queried", lines=5)
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
        
        **On the right:**  
        Import your company documents as csv, like closed incidents and user information, and initiate vector database.
        
        **On the left:**  
        Import a new alert you want analyzed as **csv**.
        
        After, press **Generate** to get a predictive summary.
        
        > *Note: It is AI-generated and may contain mistakes or incorrect analysis.*
        
        ---

        """)
    
    with gr.Row():
        with gr.Column(scale=2, variant='panel'):
            input_import = gr.File(label="Import your input csv")    
            generate_btn = gr.Button("Generate", elem_classes="btn")
            output = gr.Textbox(label="Output", lines=5)
            
            with gr.Accordion(label="debug", open=False):
                debug_metadata = gr.Textbox(label="Context rows", lines=5)
                debug_page = gr.Textbox(label="Context pages", lines=5)

                template = gr.Textbox(label="Template", value="""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an intelligent security assistant tasked with determining if an input incident is a "true positive" or "false positive."

### Definitions:
- **True Positive**: An incident that poses a real threat or indicates malicious activity, requiring immediate attention and action.
- **False Positive**: An incident that is benign and poses no real threat, typically resulting from misclassification or non-malicious behavior.

### Instructions:
1. **Analyze the Incident**: Carefully evaluate the details of the input incident provided below.
2. **Use Company Documents**: Utilize the accompanying company documents to gather context, evaluate threat indicators, and make your determination. Focus on attributes like:
   - User behavior anomalies
   - Known malicious signatures
   - Historical incident data
   - **Job title and role appropriateness**: Check if the job title in the company documents matches the assigned role in the incident. If the job title does not warrant assigning a new privileged role, classify the incident as a "true positive."
3. **Reasoning Process**:
   - Identify and explain any attributes from the documents that indicate whether the incident is malicious or benign.
   - If there are signs of malicious intent (e.g., matching known attack patterns, job title not matching privileged role assignment), classify the incident as a "true positive."
   - If the incident shows benign characteristics (e.g., known safe IPs, normal user behavior), classify it as a "false positive."

### Response Format:
1. **Classification**: Indicate whether the incident is a "true positive" or "false positive."
2. **Reasoning**: Provide a short summary of your reasoning based on evidence from the incident and company documents.
3. **Key Attributes**: List key indicators from the documents that influenced your decision.

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Here is the input incident: {incident}
Here are the company documents: {documents}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>""")
                
                use_aug = gr.Checkbox(label="Use query augmentation")
                search_type = gr.Radio(["similarity", "mmr"], value="mmr", label="Search type", info="MMR: Maximal marginal relevance optimizes for similarity to query AND diversity among selected documents.")
                k = gr.Slider(1, 10, value=5, step=1, label="k", info="Number of documents retrieved")
                gr.Markdown("Use these with mmr")
                lambda_mult = gr.Number(label="lambda_mult", info=" Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum, changes of 0.001 make a difference. (Default: 0.5)")
                fetch_k = gr.Slider(1, 50, value=50, step=1, label="fetch_k", info="Amount of documents to pass to MMR algorithm")
                
                simulator_btn = gr.Button("Generate", elem_classes="btn")
            
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
    simulator_btn.click(fn=simulatorGenerator.generate, inputs=[input, template, search_type, k, lambda_mult, fetch_k, use_aug], outputs=[output, debug_metadata, debug_page])


##########################################################################################
##########################################################################################


# Put the UI in a tabbed interface, representing two usage scenarios
app = gr.TabbedInterface(interface_list=[csvs, azure], tab_names=["Import csv", "Azure connection"], theme=theme, css=css)

proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)