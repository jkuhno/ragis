from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

import data_loader as loader


def load_context(tab, path=" "):
    if tab == "dummy":
        docs = loader.get_dummy_users() + loader.get_dummy_context()
    elif tab == "import":
        docs = loader.get_context_from_file(path)
        docs = [j for i in docs for j in i]
    
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


#### Clear ####
def clear():
    vectorstore = Chroma(
        collection_name="ragis-chroma",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )

    vectorstore._client.delete_collection(name="ragis-chroma")