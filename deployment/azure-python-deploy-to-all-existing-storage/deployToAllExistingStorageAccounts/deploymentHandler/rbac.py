# import azure.graphrbac.models
from azure.graphrbac import GraphRbacManagementClient
from azure.identity import DefaultAzureCredential

import utils

def createServicePrincipal():

    tenant_id = str(utils.get_config_from_file("tenant_id"))
    app_id = str(utils.get_config_from_file("app_id"))
    credentials = DefaultAzureCredential(exclude_environment_credential=False)

    if tenant_id and credentials and app_id:
        graphrbac_client = GraphRbacManagementClient(	
            credentials,	
            tenant_id	
        )	

    # graphrbac_client = create_basic_client(
    #     azure.graphrbac.GraphRbacManagementClient,
    #     tenant_id=tenant_id
    # )

    # # Delete the app if already exists
    # for app in graphrbac_client.applications.list(filter="displayName eq 'trendmicro_fss_app'"):
    #     graphrbac_client.applications.delete(app.object_id)

    # app = graphrbac_client.applications.create({
    #     'available_to_other_tenants': False,
    #     'display_name': 'trendmicro_fss_app',
    #     'identifier_uris': ['http://pytest_app.org'],
    #     'app_roles': [{
    #         "allowed_member_types": ["User"],
    #         "description": "Creators can create Surveys",
    #         "display_name": "SurveyCreator",
    #         "id": "1b4f816e-5eaf-48b9-8613-7923830595ad",  # Random, but fixed for tests
    #         "is_enabled": True,
    #         "value": "SurveyCreator"
    #     }]
    # })

    # # Take this opportunity to test get_objects_by_object_ids
    # objects = graphrbac_client.objects.get_objects_by_object_ids({
    #     'object_ids': [app.object_id],
    #     'types': ['Application']
    # })
    # objects = list(objects)
    # assert len(objects) == 1
    # assert objects[0].display_name == 'pytest_app'

    # apps = list(graphrbac_client.applications.list(
    #     filter="displayName eq 'pytest_app'"
    # ))
    # assert len(apps) == 1
    # assert apps[0].app_roles[0].display_name == "SurveyCreator"

        sp = graphrbac_client.service_principals.create({
            'app_id': app_id,
            'account_enabled': True
        })

        print(dir(sp))

        # Testing getting SP id by app ID
        result = graphrbac_client.applications.get_service_principals_id_by_app_id(app_id)

        print("\n\tResult - \n\t" + str(result))