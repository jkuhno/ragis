from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta
import pandas as pd


KQL_QUERY_CLOSED = """
SecurityIncident
| where TimeGenerated > ago(30d)
| where Status != "New"
| extend AlertId = tostring(AlertIds[0])
| project TimeGenerated, Title, Description, Severity, Status, AlertId, IncidentNumber
| join kind=rightanti (
SecurityAlert
| where TimeGenerated > ago(30d)
| where AlertName == "User logged in outside of Finland"
| extend props = parse_json(ExtendedProperties)
| extend Location = tostring(props['Custom Details'])
| extend Parse = parse_json(Entities)
| extend DisplayName = tostring(Parse.[0].Name)
| extend IpAddress = tostring(Parse.[1].Address)
) on $left.AlertId == $right.SystemAlertId
| project TimeGenerated, AlertName, AlertSeverity, Description, DisplayName, IpAddress, Location
"""

KQL_QUERY_ALERTS = """
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
def get_response(id, query_input):
    if query_input == "Closed incidents":
        query_ = KQL_QUERY_CLOSED
    elif query_input == "Users":
        query_ = KQL_QUERY_CLOSED
    elif query_input == "Inputs":
        query_ = KQL_QUERY_ALERTS
    else:
        query_ = query_input
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    
    response = client.query_workspace(
        workspace_id=id,
        query=query_,
        timespan=timedelta(days=4)
    )

    return response


