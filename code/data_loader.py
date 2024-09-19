import pandas as pd
from langchain_community.document_loaders import CSVLoader

# Module for data loading
# Dummy data is hard coded

dummy_incident_list = ["Bill_CA", "Bill_US", "Joel_CA"]

def get_dummy_input(input):
    if input == "Bill_CA":
        return CSVLoader(file_path='/data/scratch/sample_input/LoginOutsideFinland_Bill_CA.csv').load()[0]
    elif input == "Bill_US":
        return CSVLoader(file_path='/data/scratch/sample_input/LoginOutsideFinland_Bill_US.csv').load()[0]
    elif input == "Joel_CA":
        return CSVLoader(file_path='/data/scratch/sample_input/LoginOutsideFinland_Joel.csv').load()[0]


def get_dummy_users():
    users = pd.read_csv('/data/scratch/exportUsers_2024-9-13.csv')
    users = users.dropna(axis=1, how="all")
    users = users.to_csv('/data/scratch/exportUsers_2024-9-13.csv')
    user_docs = CSVLoader(file_path='/data/scratch/exportUsers_2024-9-13.csv').load()
    return user_docs


def get_dummy_context():
    return CSVLoader(file_path='/data/scratch/Closed Incidents/Closed_Incidents_1.csv').load()