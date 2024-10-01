from langchain.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import CSVLoader

import databases

def query_augmentation(query):
    llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct", temperature=0)

    # Step 2: Define a prompt template for query augmentation
    prompt_template = """
    You are an assistant tasked with generating different variations of a search query to help retrieve more diverse information.
    
    Original query: "{query}"
    
    Provide 3 different rephrased versions of this query that capture different ways of asking for the same or related information.
    
    Format the output as JSON with versions as keys, without any other output than the JSON.
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["query"])
    aug_chain = prompt | llm | JsonOutputParser()
    augmented_queries = aug_chain.invoke({"query" : query})
    x = [v for k, v in augmented_queries.items()]

    # return a list of versions as str
    return x


def generate(input, template_, search, k, mult, f_k, use_aug):
    
    prompt = PromptTemplate(
    template=template_,
    input_variables=["incident", "documents"],
    )

    incident = CSVLoader(file_path=input).load()[0]

    if search == "mmr":
        retriever = databases.get_retriever_with_settings(search, k, mult, f_k)
    else:
        retriever = databases.get_retriever()
        
    if use_aug:
        aug_incident = '; '.join(query_augmentation(incident.page_content))
        context = retriever.invoke(aug_incident)
    else:
        context = retriever.invoke(incident.page_content)
    
    
    
    # Chain input variables, keys match the input_variables in the PromptTemplate
    invoker = {"documents": context,
           "incident": incident,
          # "extended": user_info
          }

    # Use Nvidia AI tokens, check "https://build.nvidia.com/" for how many left
    llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct", temperature=0)


    # Shortned version of a LangChain RunnableSequence, first output is next input
    rag_chain = prompt | llm | StrOutputParser()

    generation = rag_chain.invoke(invoker)

    # Testing and debugging help
    l = []
    x = []
    for i in context:
        l.append(i.metadata)
        x.append(i.page_content)
        
    return generation, l, x


"""
old prompt
 You are an assistant tasked to reason if an input incident is a true positive or a false positive. True positives are incidents that require more attention from the user, false positives usually mean no harm.
    Use the Active Directory information and previous incidents to logically decide if input incident is malicious or not. Flag malicious as true positive and logically acceptable as false positive.
    The user wants a "true positive" or "false positive" prediction, a short summary of your reasoning and a list of key attributes you used for the reasoning.
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Here is the input incident: {incident}
    Here are the Active Directory information: {extended}
    Here are the previous incidents: {documents}
"""