"""
Modified class. Original version can be found at https://raw.githubusercontent.com/Azure-Samples/resource-manager-python-template-deployment/master/deployer.py

Modifications include
    - uuid7 instead of Haikunator, for a shorter random suffix.
    - using dynamic regions for deployment
"""

"""A deployer class to deploy a template on Azure"""
import os.path
import json
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from azure.mgmt.resource.resources.models import Deployment
from azure.mgmt.resource.resources.models import DeploymentProperties

import keyvault

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """

    def __init__(self, subscription_id, resource_group_name):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        # self.credentials = DefaultAzureCredential(exclude_environment_credential=False)

        # TODO: Store credentials in the Azure Key Vault, instead of environment variables
        # print("\nClient ID : " + str(keyvault.get_secret_from_keyvault('FSS-AUTODEPLOY-CLIENT-ID')) + "\nClient Secret : " +  str(keyvault.get_secret_from_keyvault('FSS-AUTODEPLOY-CLIENT-SECRET')))

        # self.credentials = ServicePrincipalCredentials(
        #     client_id=os.environ['AZURE_CLIENT_ID'],
        #     secret=os.environ['AZURE_CLIENT_SECRET'],
        #     tenant=os.environ['AZURE_TENANT_ID']
        # )
        self.credentials = ClientSecretCredential(
            client_id=os.environ['AZURE_CLIENT_ID'],
            client_secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant_id=os.environ['AZURE_TENANT_ID']       
        )
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

    def deploy(self, azure_location, stack_type, stack_params={}):
        """Deploy the template to a resource group."""
        self.client.resource_groups.create_or_update(
            self.resource_group_name,
            {
                'location': azure_location
            }
        )

        template_file_name = None
        if stack_type == "scanner":
            template_file_name = "FSS-Scanner-Stack-Template.json"
        elif stack_type == "storage":
            template_file_name = "FSS-Storage-Stack-Template.json"

        template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file_name)
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)        

        parameters = {}
        if stack_params:
            parameters.update(stack_params)
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = DeploymentProperties(
            mode = DeploymentMode.incremental,
            template = template,
            parameters = parameters
        )

        # TODO: Tag your deployments so you can keep track
        deployment_async_operation = self.client.deployments.begin_create_or_update(
            resource_group_name = self.resource_group_name,
            deployment_name = self.resource_group_name + '-dep',
            parameters = Deployment(properties = deployment_properties)
        )
        deployment_async_operation.wait()

        deployment_outputs = self.client.deployments.get(
            resource_group_name = self.resource_group_name,
            deployment_name = self.resource_group_name + '-dep'
        )

        return deployment_outputs.properties.outputs 

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group_name)
