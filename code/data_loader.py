import pandas as pd
from langchain_community.document_loaders import CSVLoader

import test_data

# Module for data loading
# Dummy data is hard coded in test_data


# Provide the sample alert UI names in a list
dummy_incident_list = test_data.get_sample_alerts("list")

# Return a list containing lists of documents, one inner list per imported file path
def get_context_from_file(path):
    docs = []
    for i in path:
        df = pd.read_csv(i, index_col=[0])
        df = df.dropna(axis=1, how="all")
        df.to_csv(i)
        docs.append(CSVLoader(file_path=i).load())
    return docs

# Load and return the sample alert as LangChain Document, input_name is the choice from UI made by user (value from "dummy_incident_list")
def get_input_alert(input_name):
    if input_name in dummy_incident_list:
        # as pandas df
        input = test_data.get_sample_alerts(input_name)
        input.to_csv(f'/data/tmp/alert_{input_name}.csv')
        return CSVLoader(file_path=f'/data/tmp/alert_{input_name}.csv').load()[0]
    else:
        return CSVLoader(file_path=input_name).load()[0]
    
    """
    Old execution
    
    # Check if the input exists in the dictionary
    if input_name in sample_inputs:
        # Get the corresponding filename
        filename = sample_inputs[input_name]["filename"]
        # Load the file using CSVLoader and return the result
        return CSVLoader(file_path=f'{paths["sample_inputs_path"]}{filename}').load()[0]
    else:
        raise ValueError(f"Invalid sample input name: {input_name}")
    """

# Load and return the sample alert as Pandas DataFrame, input_name is the choice from UI made by user (value from "dummy_incident_list")
def get_input_as_pd(input_name):
    if input_name in dummy_incident_list:
        return test_data.get_sample_alerts(input_name)
    else:
        return pd.read_csv(input_name)
    
    
    
    """
    Old execution
    
    # Check if the input exists in the dictionary
    if input_name in sample_inputs:
        # Get the corresponding filename
        filename = sample_inputs[input_name]["filename"]
        # Load the file using CSVLoader and return the result
        return pd.read_csv(f'{paths["sample_inputs_path"]}{filename}', index_col=[0])
    else:
        raise ValueError(f"Invalid sample input name: {input_name}")
    """

# Return user information as either LangChain Document or Pandas DataFrame, corresponding to the "output_type"
def get_dummy_users(output_type = "Document"):
    users = test_data.get_sample_users()
    if output_type == "Document":
        users.to_csv('/data/tmp/users.csv')
        return CSVLoader(file_path='/data/tmp/users.csv').load()
    elif output_type == "DataFrame":
        return users

    """
    Old execution
    
    users = pd.read_csv(paths["user_info"], index_col=[0])
    users = users.dropna(axis=1, how="all")
    if output_type == "Document":
        users = users.to_csv(paths["user_info"])
        user_docs = CSVLoader(file_path=paths["user_info"]).load()
        return user_docs
    elif output_type == "DataFrame":
        return users
    else:
        raise ValueError(f"Invalid output type: {output_type}")
    """

# Return dummy closed incidents, either LangChain Document or Pandas DataFrame
def get_dummy_context(output_type = "Document"):
    docs = test_data.get_closed_incidents()
    if output_type == "Document":
        docs.to_csv('/data/tmp/docs.csv')
        return CSVLoader(file_path='/data/tmp/docs.csv').load()
    elif output_type == "DataFrame":
        return docs
    
    """
    Old execution
    
    if output_type == "Document":
        return CSVLoader(file_path=paths["closed_incidents"]).load()
    elif output_type == "DataFrame":
        return pd.read_csv(paths["closed_incidents"])
    else:
        raise ValueError(f"Invalid output type: {output_type}")
    """