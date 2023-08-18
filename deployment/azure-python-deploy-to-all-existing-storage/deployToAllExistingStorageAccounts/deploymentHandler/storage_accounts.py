import utils
import logging

# get_storage_accounts: Provides a list of all Azure Storage Accounts in this subscription with the Tag AutoDeployFSS = true
def get_storage_accounts(FSS_LOOKUP_TAG):

    storage_accounts_json_response = utils.azure_cli_run_command('storage account list')

    logging.info("Tag Lookup: " + FSS_LOOKUP_TAG)

    azure_storage_account_list = []

    if storage_accounts_json_response:

        for storage_account in storage_accounts_json_response:

            if storage_account["tags"]:
                
                if FSS_LOOKUP_TAG in storage_account["tags"].keys():

                    if storage_account["tags"][FSS_LOOKUP_TAG]:

                        azure_storage_account_list.append({"name": storage_account["name"], "location": storage_account["location"], "tags": storage_account["tags"], "id": storage_account["id"]})        

    return azure_storage_account_list