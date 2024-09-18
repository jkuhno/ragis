import gradio as gr
import os

import pandas as pd
from langchain_community.document_loaders import CSVLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser


bill_ca = CSVLoader(file_path='/data/scratch/sample_input/LoginOutsideFinland_Bill_CA.csv').load()[0]
bill_us = CSVLoader(file_path='/data/scratch/sample_input/LoginOutsideFinland_Bill_US.csv').load()[0]
joel_ca = CSVLoader(file_path='/data/scratch/sample_input/LoginOutsideFinland_Joel.csv').load()[0]


users = pd.read_csv('/data/scratch/exportUsers_2024-9-13.csv')
users = users.dropna(axis=1, how="all")
users = users.to_csv('/data/scratch/exportUsers_2024-9-13.csv')
user_docs = CSVLoader(file_path='/data/scratch/exportUsers_2024-9-13.csv').load()


# Context from Entra ID
vectorstore_users = Chroma.from_documents(
    documents=user_docs,
    collection_name="ragis-chroma-users",
    embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
)
retriever_users = vectorstore_users.as_retriever(search_kwargs={'k': 1})


# Context from previously closed incidents
context = CSVLoader(file_path='/data/scratch/Closed Incidents/Closed_Incidents_1.csv').load()

vectorstore = Chroma.from_documents(
    documents=context,
    collection_name="ragis-chroma",
    embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
)
retriever = vectorstore.as_retriever()


def test(input):
    if input == "bill_ca":
        incident = bill_ca
    elif input == "bill_us":
        incident = bill_us
    elif input == "joel_ca":
        incident = joel_ca
    
    prompt = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an assistant tasked to reason if an input incident is a true positive or a false positive. True positives are incidents that require more attention from the user, false positives usually mean no harm.
    Use the Active Directory information and previous incidents to logically decide if input incident is malicious or not. Flag malicious as true positive and logically acceptable as false positive.
    The user wants a "true positive" or "false positive" prediction, a short summary of your reasoning and a list of key attributes you used for the reasoning.
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Here is the input incident: {incident}
    Here are the Active Directory information: {extended}
    Here are the previous incidents: {documents}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["incident", "documents", "extended"],
    )


    # Documents retrieved from vector store, that are the best match for the question
    context_docs = retriever.invoke(incident.page_content)


    context_users = retriever_users.invoke(incident.page_content)

    # Chain input variables, keys match the input_variables in the PromptTemplate
    invoker = {"documents": context_docs,
           "incident": incident,
           "extended": context_users
          }

    # Use Nvidia AI tokens, check "https://build.nvidia.com/" for how many left
    llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct", temperature=0)


    # Shortned version of a LangChain RunnableSequence, first output is next input
    rag_chain = prompt | llm | StrOutputParser()

    generation = rag_chain.invoke(invoker)
    
    return generation


with gr.Blocks() as app:
    with gr.Row():
        input = gr.Radio(["bill_ca", "bill_us", "joel_ca"])
    with gr.Row():
        output = gr.Textbox(label="Output")
    with gr.Row():
        btn = gr.Button("Go")
        btn.click(fn=test, inputs=input, outputs=output, api_name="greet")



proxy_prefix = os.environ.get("PROXY_PREFIX")
app.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)
