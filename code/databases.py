from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

import data_loader as loader

def load_context(tab, path=" "):
    if tab == "dummy":
        docs = loader.get_dummy_users() + loader.get_dummy_context()
    elif tab == "import":
        docs = loader.get_context_from_file(path)
    
    vectorstore = Chroma.from_documents(
        documents=docs,
        collection_name="ragis-chroma",
        embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore

def get_retriever():
    vectorstore = Chroma(
        collection_name="ragis-chroma",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore.as_retriever()
    
"""
#### Users ####
###############

def load_users_vectorstore():
    vectorstore_users = Chroma.from_documents(
        documents=loader.get_dummy_users(),
        collection_name="ragis-chroma-users",
        embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore_users


def get_users_retriever():
    vectorstore_users = Chroma(
        collection_name="ragis-chroma-users",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore_users.as_retriever(search_kwargs={'k': 3})


#### Closed incidents ####
##########################

def load_context_vectorstore():
    vectorstore = Chroma.from_documents(
        documents=loader.get_dummy_context(),
        collection_name="ragis-chroma",
        embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore


def get_context_retriever():
    vectorstore = Chroma(
        collection_name="ragis-chroma",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore.as_retriever()
"""

#### Clear ####
###############

def clear():
    vectorstore = Chroma(
        collection_name="ragis-chroma",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    """
    vectorstore_users = Chroma(
        collection_name="ragis-chroma-users",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    """
    vectorstore._client.delete_collection(name="ragis-chroma")
    # vectorstore_users._client.delete_collection(name="ragis-chroma-users")