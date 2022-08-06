import locations

def get_geographies_from_storage_accounts(azure_storage_account_list, azure_supported_locations_obj_by_geography_groups_dict):

    unique_scanner_stack_list = []

    for storage_account in azure_storage_account_list:

        azure_geography_group = get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

        # logging.info("Storage Account - " + str(azure_geography_group))

        if azure_geography_group not in unique_scanner_stack_list:
            unique_scanner_stack_list.append(azure_geography_group)

    return unique_scanner_stack_list

def get_geography_group_from_location(azure_location_name, azure_geography_groups_dict): # eastus, { azure_geography_groups_dict ... }

    for azure_geography_group_item in azure_geography_groups_dict:
        for azure_location in azure_geography_groups_dict[azure_geography_group_item]:
            if azure_location_name == azure_location["name"]:
                return azure_geography_group_item
    return None

def build_geographies_map_dict():

    geography_map_dict = {}

    azure_supported_locations_obj_by_geography_groups_dict = locations.get_azure_supported_locations()

    for azure_geography_group in azure_supported_locations_obj_by_geography_groups_dict:
        if azure_geography_group not in geography_map_dict:
            geography_map_dict.update({azure_geography_group: []})

    # Remove any logical Azure Locations in Map Dictionary
    geography_map_dict.pop("logical")

    return geography_map_dict

