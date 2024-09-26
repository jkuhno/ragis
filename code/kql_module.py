from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta
import pandas as pd


KQL_QUERY = """
SecurityAlert
| extend props = parse_json(ExtendedProperties)
| extend Location = tostring(props['Custom Details'])
| extend Parse = parse_json(Entities)
| extend DisplayName = tostring(Parse.[0].Name)
| extend IpAddress = tostring(Parse.[1].Address)
| project TimeGenerated, AlertName, AlertSeverity, Description, DisplayName, IpAddress, Location
"""


# Authenticate via envs
# Return LogsQueryResult object
# https://learn.microsoft.com/en-gb/python/api/azure-monitor-query/azure.monitor.query.logsqueryresult?view=azure-python-preview
def get_response(id):
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    
    response = client.query_workspace(
        workspace_id=id,
        query=KQL_QUERY,
        timespan=timedelta(days=4)
    )

    return response


# Return first data table as pandas DataFrame
def response_as_df(id):
    response = get_response(id)
    data_list = []
    for table in response.tables:
        # Extract columns and rows from the response
        columns = [col for col in table.columns]
        rows = table.rows
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(rows, columns=columns)
        data_list.append(df)

    return data_list[0]