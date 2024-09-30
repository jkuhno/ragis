from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta

# Azure connections


# Default KQL for context closed incidents querying
KQL_QUERY_CLOSED = """
SecurityIncident
| where Status == "Closed"
| extend AlertId = tostring(AlertIds[0])
| project TimeGenerated, IncidentNumber, IncidentTitle=Title, IncidentDescription=Description, IncidentSeverity=Severity, Classification, ClassificationComment, ClassificationReason, ClosedTime, AlertId
| join kind=inner (
SecurityAlert
| extend Parse = parse_json(Entities)
| extend entities1 = tostring(Parse.[0])
| extend entities2 = tostring(Parse.[1])
| extend properties = parse_json(ExtendedProperties)
| extend Location = tostring(properties['Custom Details'])
) on $left.AlertId==$right.SystemAlertId
| project TimeGenerated, IncidentNumber, IncidentTitle, IncidentDescription, IncidentSeverity, Classification, ClassificationComment, ClassificationReason, ClosedTime, entities1, entities2, Location
"""

# Query for new incidents
KQL_QUERY_ALERTS = """
SecurityIncident
| where Status == "New"
| extend AlertId = tostring(AlertIds[0])
| project TimeGenerated, IncidentNumber, IncidentTitle=Title, IncidentDescription=Description, IncidentSeverity=Severity, IncidentStatus=Status, AlertId
| join kind=inner (
SecurityAlert
| extend Parse = parse_json(Entities)
| extend entities1 = tostring(Parse.[0])
| extend entities2 = tostring(Parse.[1])
| extend properties = parse_json(ExtendedProperties)
| extend Location = tostring(properties['Custom Details'])
) on $left.AlertId==$right.SystemAlertId
| project TimeGenerated, IncidentNumber, IncidentTitle, IncidentDescription, IncidentSeverity, IncidentStatus, entities1, entities2, Location
"""


# Authenticate via envs
# Return LogsQueryResult object
# https://learn.microsoft.com/en-gb/python/api/azure-monitor-query/azure.monitor.query.logsqueryresult?view=azure-python-preview
def get_response(id, query_input, time_span):
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
        timespan=timedelta(days=time_span)
    )

    return response

