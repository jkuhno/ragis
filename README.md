# RAGIS (Retrieval-Augmented Generation Incident Summary)
Our project, RAGIS (Retrieval-Augmented Generation Incident Summary), helps security analysts determine whether an incident is false or if the incident needs further investigation. It leverages generative AI and company data such as Microsoft Entra ID user details and previously closed incidents to make accurate predictions, saving valuable time and reducing the noise from false incidents.

## Inspiration
Security analysts often spend significant time investigating false positives, which can lead to inefficiencies. Studies show that nearly a third of their time is spent on incidents that pose no actual threat. This creates alert fatigue and slows down response times, motivating us to create a solution that reduces this burden and helps analysts focus on real security threats.

## How we built it
We used NVIDIA AI Workbench with LangChain to build a retrieval-augmented generation (RAG) system. Closed incidents and user data are embedded in a Chroma vector database, and a Llama 3.1 70B instruct model is used to predict whether an incident is false or true positive.

## Getting Started

### Integrating RAGIS with Azure
