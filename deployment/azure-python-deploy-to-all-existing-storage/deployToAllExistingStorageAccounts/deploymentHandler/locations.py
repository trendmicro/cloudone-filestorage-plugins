from azure.mgmt.subscription import SubscriptionClient
from azure.identity import ClientSecretCredential

import os
import utils
import random

# get_azure_recommended_location_by_geography_group - Pick one Azure recommended location in the geography location. 
def get_azure_recommended_location_by_geography_group(azure_geography_group, azure_geography_groups_dict, fss_supported_regions_list):
    for azure_geography_group_item in azure_geography_groups_dict:
        if azure_geography_group == azure_geography_group_item:

            temp_azure_geography_group_list = []
            for azure_location in azure_geography_groups_dict[azure_geography_group]:

                if azure_location["metadata"]["regionCategory"] and azure_location["metadata"]["regionCategory"] == "Recommended" and azure_location["name"] in fss_supported_regions_list:

                    temp_azure_geography_group_list.append(azure_location)

            return temp_azure_geography_group_list[random.randint(0, len(temp_azure_geography_group_list)-1)]["name"]

# get_azure_supported_locations - Lists all supported locations for Azure in the current subscription.
def get_azure_supported_locations():
    azure_locations_list = utils.azure_cli_run_command('account list-locations')

    azure_supported_locations_obj_by_geography_groups = {}

    for azure_location in azure_locations_list:
        if azure_location["metadata"]["geographyGroup"] and utils.trim_spaces(azure_location["metadata"]["geographyGroup"]) not in azure_supported_locations_obj_by_geography_groups.keys():
            azure_supported_locations_obj_by_geography_groups.update({utils.trim_spaces(azure_location["metadata"]["geographyGroup"]): []})
        elif not azure_location["metadata"]["geographyGroup"]:
            azure_supported_locations_obj_by_geography_groups.update({"logical": []})

    for azure_location in azure_locations_list:
        if azure_location["metadata"]["regionType"] == "Physical":
            azure_supported_locations_obj_by_geography_groups[utils.trim_spaces(azure_location["metadata"]["geographyGroup"])].append(azure_location)
        else:
            azure_supported_locations_obj_by_geography_groups["logical"].append(azure_location)

    return azure_supported_locations_obj_by_geography_groups

# get_azure_location_detail - Lists Azure location detail
def get_azure_location_detail(azure_location_name):
    azure_locations_list = utils.azure_cli_run_command('account list-locations')

    for azure_location in azure_locations_list:
        if azure_location["name"] == azure_location_name:
            return azure_location

# get_azure_supported_locations_sdk - Lists all supported locations for Azure in the current subscription via Azure SDK.
def get_azure_supported_locations_sdk():

    # credentials =  ServicePrincipalCredentials(
    #     client_id=os.environ['AZURE_CLIENT_ID'],
    #     secret=os.environ['AZURE_CLIENT_SECRET'],
    #     tenant=os.environ['AZURE_TENANT_ID']
    # )

    credentials =  ClientSecretCredential(
        client_id=os.environ['AZURE_CLIENT_ID'],
        client_secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant_id=os.environ['AZURE_TENANT_ID']       
    )

    # credentials = DefaultAzureCredential(exclude_environment_credential=False)
    subscription_client = SubscriptionClient(credentials, api_version='2021-01-01')

    subscription_id = utils.get_subscription_id()

    azure_locations_iter = subscription_client.subscriptions.list_locations(subscription_id)    
    
    azure_locations_list = []
    for location in azure_locations_iter:
        azure_locations_list.append(location.name)

    return azure_locations_list