from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

import data_loader as loader


def load_context(path=""):
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

def get_retriever_with_settings(search, k, mult, f_k):
    vectorstore = Chroma(
        collection_name="ragis-chroma",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )
    return vectorstore.as_retriever(
        search_type=search,
        search_kwargs={'k': k, 'lambda_mult': mult, "fetch_k": f_k}
)


#### Clear ####
def clear():
    vectorstore = Chroma(
        collection_name="ragis-chroma",
        embedding_function=NVIDIAEmbeddings(model='NV-Embed-QA'),
        persist_directory="/project/data/scratch",
    )

    vectorstore._client.delete_collection(name="ragis-chroma")