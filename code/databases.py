from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

import data_loader as loader


def get_users_retriever():
    vectorstore_users = Chroma.from_documents(
        documents=loader.get_dummy_users(),
        collection_name="ragis-chroma-users",
        embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
    )
    return vectorstore_users.as_retriever(search_kwargs={'k': 3})

def get_context_retriever():
    vectorstore = Chroma.from_documents(
        documents=loader.get_dummy_context(),
        collection_name="ragis-chroma",
        embedding=NVIDIAEmbeddings(model='NV-Embed-QA'),
    )
    return vectorstore.as_retriever()

