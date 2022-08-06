import json
import logging
from http.client import responses
import urllib3
# http = urllib3.PoolManager()
urllib3.disable_warnings()
http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

import utils

def filter_stacks_by_subscription_id(subscription_id, cloudone_fss_stacks_output):    

    temp_stacks_output_list = []
    for stack in cloudone_fss_stacks_output["stacks"]:             
        if utils.get_subscription_id_from_resource_group_id(stack["details"]["resourceGroupID"]) != subscription_id:
            temp_stacks_output_list.append(stack)
        
    for stack in temp_stacks_output_list:
        cloudone_fss_stacks_output["stacks"].remove(stack)
    return cloudone_fss_stacks_output

def get_scanner_stacks():
    
    r = None
    try:
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        
        if region and api_key:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            r = http.request(
                "GET",
                cloudone_fss_api_url + "/stacks?provider=azure&type=scanner",
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },

            )

            if r.status == 200:
                return json.loads(r.data)
            else:                
                logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
                raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:        
        if r:
            logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
            raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
        else:
            logging.error("HTTP Request failure. Check the logs for more information.")
            raise Exception("HTTP Request failure. Check the logs for more information.")

def get_storage_stacks():
    
    r = None
    try:    
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()

        if region and api_key:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)            

            r = http.request(
                "GET",
                cloudone_fss_api_url + "/stacks?provider=azure&type=storage",
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                }
            )

            if r.status == 200:
                return json.loads(r.data)
            else:
                logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
                raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:        
        if r:
            logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
            raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
        else:
            logging.error("HTTP Request failure. Check the logs for more information.")
            raise Exception("HTTP Request failure. Check the logs for more information.")

def map_scanner_stacks_to_azure_locations():

    subscription_id = utils.get_subscription_id()

    existing_scanner_stacks_dict = filter_stacks_by_subscription_id(subscription_id, get_scanner_stacks())

    if existing_scanner_stacks_dict:
        locationsDict = {}
        for scanner_stack in existing_scanner_stacks_dict["stacks"]:

            if scanner_stack["status"] == "ok":

                if scanner_stack["details"]["region"] not in locationsDict:
                    locationsDict.update({scanner_stack["details"]["region"]: []})
                
                locationsDict[scanner_stack["details"]["region"]].append(scanner_stack)

        return locationsDict
    return None

def get_associated_storage_stacks_to_scanner_stack(scanner_stack_uuid):
    
    r = None
    try:    
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        
        if region and api_key:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            r = http.request(
                "GET",
                cloudone_fss_api_url + "/stacks?provider=azure&type=storage&scannerStack=" + scanner_stack_uuid,
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },

            )
            if r.status == 200:
                return json.loads(r.data)
            else:
                logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
                raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:
        if r:
            logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
            raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
        else:
            logging.error("HTTP Request failure. Check the logs for more information.")
            raise Exception("HTTP Request failure. Check the logs for more information.")

def register_scanner_stack_with_cloudone(resource_group_id, tenant_id):

    r = None
    try:    
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        
        if region and api_key:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            request_data = {
                'type': 'scanner',
                'provider': 'azure',
                'details': {
                    'resourceGroupID': resource_group_id,
                    'tenantID': tenant_id
                }
            }

            r = http.request(
                "POST",
                cloudone_fss_api_url + "/stacks",
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },    
                body=json.dumps(request_data)        
            )
            if r.status == 200:
                return json.loads(r.data)["stackID"]
            else:
                logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
                raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:        
        if r:
            logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
            raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
        else:
            logging.error("HTTP Request failure. Check the logs for more information.")
            raise Exception("HTTP Request failure. Check the logs for more information.")        

def register_storage_stack_with_cloudone(cloudone_scanner_stack_id, resource_group_id, tenant_id):

    r = None
    try:    
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        
        if region and api_key:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            request_data = {
                'type': 'storage',
                'provider': 'azure',
                'scannerStack': cloudone_scanner_stack_id,
                'details': {
                    'resourceGroupID': resource_group_id,
                    'tenantID': tenant_id
                }
            }

            r = http.request(
                "POST",
                cloudone_fss_api_url + "/stacks",
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },    
                body=json.dumps(request_data)        
            )
            if r.status == 200:
                return json.loads(r.data)
            else:      
                logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")         
                raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:        
        if r:
            logging.error("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")  
            raise Exception("HTTP Request failure (code: " + str(r.status) + ". Message: " + str(responses[r.status]) + "). Check the logs for more information.")
        else:
            logging.error("HTTP Request failure. Check the logs for more information.")  
            raise Exception("HTTP Request failure. Check the logs for more information.")   
