# Copyright (c) 2024 Jani Kuhno, Joel Kataja
# https://www.apache.org/licenses/LICENSE-2.0.txt License.
# Author: Jani Kuhno

# Module for the LLm chain


from langchain.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import CSVLoader

import databases

def generate(input):
    
    prompt = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|>
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
   - **Job title and role appropriateness**: Check if the job title in the company documents matches the assigned role in the incident. If the job title does not warrant assigning a new privileged role, classify the incident as a "true positive."- 
**Login location**: Check if the previous incidents indicate a strong reason for logging in outside of Finland, otherwise classify the incident as a "true positive."
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
<|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["incident", "documents"],
    )

    incident = CSVLoader(file_path=input).load()[0]

    retriever = databases.get_retriever_with_settings("mmr", 5, 0.534, 50)
    context = retriever.invoke(incident.page_content)
    
    # Chain input variables, keys match the input_variables in the PromptTemplate
    invoker = {"documents": context,
           "incident": incident,
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
