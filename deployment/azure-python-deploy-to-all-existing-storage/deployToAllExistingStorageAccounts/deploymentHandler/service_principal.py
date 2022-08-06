import utils

def query_service_principal(appId):
    sp_list = utils.azure_cli_run_command('ad sp list --all')
    for sp_item in sp_list:
        if sp_item["appId"] == appId:
            return sp_item["id"]
    return None

def get_service_principal_id(app_id):
    service_principal_id = query_service_principal(app_id)

    if not service_principal_id:
        service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)                
    # rbac.createServicePrincipal()

    return service_principal_id