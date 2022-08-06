from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import utils

def get_secret_from_keyvault(secret_key):
    keyvault_uri = str(utils.get_config_from_file('keyvault_uri'))
    if keyvault_uri:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=keyvault_uri, credential=credential)
        return secret_client.get_secret(secret_key)
    return None

def put_secret_into_keyvault(secret_key, secret_value):
    keyvault_uri = str(utils.get_config_from_file('keyvault_uri'))
    if keyvault_uri:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=keyvault_uri, credential=credential)
        secret_client.set_secret(name=secret_key, value=secret_value)
        return True
    return None