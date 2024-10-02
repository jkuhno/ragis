# Copyright (c) 2024 Jani Kuhno, Joel Kataja
# https://www.apache.org/licenses/LICENSE-2.0.txt License.
# Author: Jani Kuhno, Joel Kataja

# Module for querying Entra ID user information from Azure


from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
import pandas as pd
import asyncio


QUERY_PARAMS = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
    select=['userPrincipalName',
            'displayName',
            'givenName',
            'surname',
            'jobTitle',
            'department',
            'usageLocation',
            'accountEnabled',
            'state','country',
            'createdDateTime'
           ]
)

async def get_users(data_type):
    credential = DefaultAzureCredential()
    client = GraphServiceClient(credential)
    
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credential, scopes)
    
    # Get all Entra ID users
    
    config = RequestConfiguration(
        query_parameters=QUERY_PARAMS
    )
    
    users = await graph_client.users.get(config)
    
    user_list = []
    for user in users.value:
        x = {
            'userPrincipalName': user.user_principal_name,
            'displayName': user.display_name,
            'givenName': user.given_name,
            'surname': user.surname,
            'jobTitle': user.job_title,
            'department': user.department,
            'usageLocation': user.usage_location,
            'accountEnabled': user.account_enabled,
            'state': user.state,
            'country': user.country,
            'createdDateTime': user.created_date_time
        }
        user_list.append(x)
    
    user_df = pd.DataFrame(user_list)
    if data_type == "csv":
        user_df.to_csv("/data/tmp/azure_users")
        return "/data/tmp/azure_users"

    return user_df