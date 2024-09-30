import pandas as pd
from langchain_community.document_loaders import CSVLoader

import kql_module as kql

# Module for transforming data from a format to another

# Converts a response from Log Analytics kql alert query into a list of tuples [(friendly_alert_name, csv_path),...]
#
#     input_response: LogsQueryClient.query_workspace response(s) as a list
#
#     return: list of tuples [(friendly_name, csv_path),...]
def kql_input_alert_tuple(input_response):
    df = response_as_df(input_response[0])
    series_list = [row for row in df[0].iterrows()]
    l = []
    for tuples in series_list:
        l.append(pd.DataFrame(tuples[1]).T)
    incidentNumber = [items["IncidentNumber"].values[0] for items in l]
    incidentTitle = [items["IncidentTitle"].values[0] for items in l]
    for idx, item in enumerate(incidentTitle):
        incidentTitle[idx] = str(incidentNumber[idx]) + f" {incidentTitle[idx]}"
    for idx, df in enumerate(l):
        df.to_csv(f'/data/tmp/azure_input_{idx}')
        l[idx] = f'/data/tmp/azure_input_{idx}'
        l[idx] = (incidentTitle[idx], l[idx])
    return l


# Converts a list of responses from Log Analytics kql query into csvs
# 
#     responses: list of responses
#     query_name: a list of strings indicating the name of the document 
#
#     return: list of csv file paths
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
        

# Convert a kql response to a Pandas DataFrame
#
#     response: LogsQueryClient.query_workspace response
#
#     return: list of all response tables as DataFrames
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

