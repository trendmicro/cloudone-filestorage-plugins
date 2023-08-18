# import logging
# from azure.mgmt.resource import ResourceManagementClient
# from azure.identity import AzureCliCredential

# def create_resource_group(subscription_id, resource_group_name, azure_location):

#     # Acquire a credential object using CLI-based authentication.
#     credential = AzureCliCredential()

#     # Obtain the management object for resources.
#     resource_client = ResourceManagementClient(credential, subscription_id)

#     # Provision the resource group.
#     resource_group = resource_client.resource_groups.create_or_update(
#         resource_group_name,
#         {
#             "location": azure_location
#         }
#     )

#     logging.info(f"Provisioned resource group {resource_group.name} in the {resource_group.location} region")

#     return resource_group_name