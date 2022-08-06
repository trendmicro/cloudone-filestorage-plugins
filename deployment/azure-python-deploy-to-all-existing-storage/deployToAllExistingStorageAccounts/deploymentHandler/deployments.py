import logging

import utils
import locations
import geographies
import service_principal
import cloudone_fss_api

from Deployer import Deployer

def deploy_fss_scanner_stack(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, azure_location, fss_supported_regions_list, azure_storage_account_name=None, scanner_stack_name=None, resource_group_name=None, geography_group_name=None):

    # File Storage Security Scanner Stack deployment templates can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Scanner-Stack-Template.json or in the ./templates directory

    app_id = str(utils.get_config_from_file("app_id"))
    cloudone_region = str(utils.get_cloudone_region())

    if app_id and cloudone_region:

        if azure_location not in fss_supported_regions_list:

            logging.info("Azure location (" + azure_location + ") is not part of the FSS supported regions. Choosing the next Azure recommended location in the same geography.")
            geography_group_name = geographies.get_geography_group_from_location(azure_location, azure_supported_locations_obj_by_geography_groups_dict)

            azure_location = locations.get_azure_recommended_location_by_geography_group(geography_group_name, azure_supported_locations_obj_by_geography_groups_dict, fss_supported_regions_list)
            logging.info("New Azure location: " + azure_location)

            scanner_stack_name = "fss-scanner-" + utils.trim_location_name(azure_location) + "-" + utils.trim_resource_name(azure_storage_account_name, 12, 12) + "-autodeploy"

        if not geography_group_name:
            geography_group_name = geographies.get_geography_group_from_location(azure_location, azure_supported_locations_obj_by_geography_groups_dict)

        if not scanner_stack_name:            
            scanner_stack_name = "fss-scanner-" + geography_group_name + "-" + azure_location + "-geo-autodeploy"
        if not resource_group_name:
            resource_group_name = scanner_stack_name + "-rg"

        logging.info("Initializing the Deployer class with subscription id: {}, resource group: {} ...".format(subscription_id, resource_group_name))

        service_principal_id = service_principal.get_service_principal_id(app_id)

        scanner_stack_params = {
            'FileStorageSecurityServicePrincipalID': service_principal_id,
            'CloudOneRegion': cloudone_region,
            'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
            'Version': 'latest',
            'SharedAccessSignature': ''
        }

        # Initialize the deployer class
        deployer = Deployer(subscription_id, resource_group_name)

        # Deploy the template
        logging.info("Beginning the deployment...")
        
        deployment_outputs = deployer.deploy(azure_location, "scanner", scanner_stack_params)

        cloudone_scanner_stack_id = cloudone_fss_api.register_scanner_stack_with_cloudone(deployment_outputs["scannerStackResourceGroupID"]["value"], deployment_outputs["tenantID"]["value"])
        deployment_outputs.update({'cloudOneScannerStackId': cloudone_scanner_stack_id})

        logging.info("Done deploying!!")

        return deployment_outputs

def deploy_fss_storage_stack(subscription_id, storage_account, cloudone_scanner_stack_id, scanner_identity_principal_id, scanner_queue_namespace, storage_stack_name=None, resource_group_name=None):

    # File Storage Security Storage Stack deployment template can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Storage-Stack-Template.json or in the ./templates directory

    app_id = str(utils.get_config_from_file("app_id"))
    cloudone_region = str(utils.get_cloudone_region())

    if not storage_stack_name:
        storage_stack_name = "fss-storage-" + utils.trim_location_name(storage_account["location"]) + "-" + utils.trim_resource_name(storage_account["name"], 12, 12) +  "-autodeploy"

    if not resource_group_name:
        resource_group_name = storage_stack_name + "-rg"

    logging.info("Initializing the Deployer class with subscription id: {}, resource group: {}...".format(subscription_id, resource_group_name))

    service_principal_id = service_principal.query_service_principal(app_id)

    # TODO: Check for Azure SDK RBAC Create Service Principal ID
    if not service_principal_id:
        service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)

    logging.info("service_principal_id - " + str(service_principal_id))

    storage_stack_params = {
        'FileStorageSecurityServicePrincipalID': service_principal_id,
        'CloudOneRegion': cloudone_region,
        'ScannerIdentityPrincipalID': scanner_identity_principal_id,
        'ScannerQueueNamespace': scanner_queue_namespace,
        'BlobStorageAccountResourceID': storage_account["id"],
        'BlobSystemTopicExist': 'No',
        'BlobSystemTopicName': 'BlobEventTopic-' + utils.trim_resource_name(storage_account["name"], 40, 40),
        'UpdateScanResultToBlobMetadata': 'Yes',
        'ReportObjectKey': 'No',
        'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
        'Version': 'latest',
        'SharedAccessSignature': ''
    }

    # Initialize the deployer class
    deployer = Deployer(subscription_id, resource_group_name)

    logging.info("Beginning the deployment...")
    # Deploy the template
    deployment_outputs = deployer.deploy(storage_account["location"], "storage", storage_stack_params)

    cloudone_fss_api.register_storage_stack_with_cloudone(cloudone_scanner_stack_id, deployment_outputs["storageStackResourceGroupID"]["value"], deployment_outputs["tenantID"]["value"])

    logging.info("Done deploying!!")

    return deployment_outputs

def build_geography_dict(azure_supported_locations_obj_by_geography_groups_dict, azure_storage_account_list):
    # Inventory of existing storage accounts
    # unique_storage_account_geographies = geographies.get_geographies_from_storage_accounts(azure_storage_account_list, azure_supported_locations_obj_by_geography_groups_dict)

    # Scanner Stack Map
    scanner_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()  

    # Storage Stacks Map
    storage_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()      

    # Populate the Scanner stack map by geographies
    # Inventory of existing FSS scanner stacks by Azure location
    existing_scanner_stacks_by_location = cloudone_fss_api.map_scanner_stacks_to_azure_locations()        

    if existing_scanner_stacks_by_location:

        # logging.info("Scanner Stack Locations: " + str(existing_scanner_stacks_by_location))

        for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

            scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stack_by_location, azure_supported_locations_obj_by_geography_groups_dict)

            scanner_stacks_map_by_geographies_dict[scanner_stack_geography] = existing_scanner_stacks_by_location[existing_scanner_stack_by_location]

    # Populate the Storage stack map by geographies
    for storage_account in azure_storage_account_list:

        if existing_scanner_stacks_by_location:

            for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

                # if "storageStacks" not in existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0].keys():

                #         existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0]["storageStacks"] = []

                existing_scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0]["details"]["region"], azure_supported_locations_obj_by_geography_groups_dict)
                storage_account_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

                if existing_scanner_stack_geography == storage_account_geography:

                    temp_storage_stacks_dict = storage_stacks_map_by_geographies_dict[existing_scanner_stack_geography]                    

                    temp_storage_stacks_dict.append(storage_account)

                    storage_stacks_map_by_geographies_dict[existing_scanner_stack_geography] = temp_storage_stacks_dict

                    logging.info("Found a match... " + str(existing_scanner_stack_geography) + " = " + str(storage_account_geography))

                else:
                    logging.info("Found a mismatch... " + str(existing_scanner_stack_geography) + " ~ " + str(storage_account_geography))
        else:
            storage_account_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

            temp_storage_stacks_dict = storage_stacks_map_by_geographies_dict[storage_account_geography]                    

            temp_storage_stacks_dict.append(storage_account)

            storage_stacks_map_by_geographies_dict[storage_account_geography] = temp_storage_stacks_dict


    return scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict