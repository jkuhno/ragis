import pandas as pd
from langchain_community.document_loaders import CSVLoader

import test_data
import kql_module as kql

# Module for transforming data from a format to another
# Dummy data is hard coded in test_data


# Provide the sample alert UI names in a list
dummy_incident_list = test_data.get_sample_alerts("list")

def kql_input_alert_tuple(input_response):
    df = response_as_df(input_response[0])
    series_list = [row for row in df[0].iterrows()]
    l = []
    for tuples in series_list:
        l.append(pd.DataFrame(tuples[1]).T)
    names = [items["DisplayName"].values[0] for items in l]
    alert = [items["AlertName"].values[0] for items in l]
    for idx, item in enumerate(alert):
        alert[idx] = item.replace("User", names[idx])
    for idx, df in enumerate(l):
        df.to_csv(f'/data/tmp/azure_input_{idx}')
        l[idx] = f'/data/tmp/azure_input_{idx}'
        l[idx] = (alert[idx], l[idx])
    return l


def kql_response_as_csv(responses, query_name):
    df_list = []
    for i in responses:
        df_list.append(response_as_df(i))
    df_list = [j for i in df_list for j in i]
    paths_list = []
    for idx, item in enumerate(df_list):
        item.to_csv(f'/data/tmp/azure_{query_name[idx]}')
        paths_list.append(f'/data/tmp/azure_{query_name[idx]}')
    return paths_list
        

def response_as_df(response):
    data_list = []
    for table in response.tables:
        # Extract columns and rows from the response
        columns = [col for col in table.columns]
        rows = table.rows
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(rows, columns=columns)
        data_list.append(df)

    return data_list


# Return a list containing lists of documents, one inner list per imported file path
def get_context_from_file(path):
    if not path:
        raise ValueError("No context files found, trying to initiate vb without input")
    else:
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
    

# Load and return the sample alert as Pandas DataFrame, input_name is the choice from UI made by user (value from "dummy_incident_list")
def get_input_as_pd(input_name):
    if input_name in dummy_incident_list:
        return test_data.get_sample_alerts(input_name)
    else:
        return pd.read_csv(input_name)
    
    
# Return user information as either LangChain Document or Pandas DataFrame, corresponding to the "output_type"
def get_dummy_users(output_type = "Document"):
    users = test_data.get_sample_users()
    if output_type == "Document":
        users.to_csv('/data/tmp/users.csv')
        return CSVLoader(file_path='/data/tmp/users.csv').load()
    elif output_type == "DataFrame":
        return users


# Return dummy closed incidents, either LangChain Document or Pandas DataFrame
def get_dummy_context(output_type = "Document"):
    docs = test_data.get_closed_incidents()
    if output_type == "Document":
        docs.to_csv('/data/tmp/docs.csv')
        return CSVLoader(file_path='/data/tmp/docs.csv').load()
    elif output_type == "DataFrame":
        return docs
    