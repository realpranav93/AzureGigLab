import requests
import json
import random
import logging
from azure.identity import DefaultAzureCredential

# Example 1: POST request with JSON body and headers
def call_api_post():
    # API endpoint URL

    dac = DefaultAzureCredential()
    url = "https://giglabhack.azurewebsites.net/api/CreateAzureResource"
    # url = "https://accountplan-gbhaenamd4ckcbbw.eastus2-01.azurewebsites.net/api/accountidentifier"
    # Headers
    
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer your-token-here",
        "x-functions-key": "3H5_rIyI4AYGa6mcCA2EVhYFqe0rcVvltgzHg7UeBtQVAzFuynsuOA=="
    }
    project_name = "churnpredv2"
    # Request body
    resource_ops = [
        # 1. Storage Account with public access disabled
        {
            "type": "Storage Account",
            "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/st{resource_name}",
            "body": {
                "sku": {"name": "Standard_LRS"},
                "kind": "StorageV2",
                "location": "eastus2",
                "properties": {
                    "publicNetworkAccess": "Disabled"
                }
            },
            "api_version": "2021-09-01",
            "method": "PUT"
        },
        # 2. AI Foundry (Cognitive Services) with public access disabled
        {
            "type": "AI Foundry",
            "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/cog{resource_name}",
            "body": {
                "location": "eastus2",
                "sku": {"name": "S0"},
                "kind": "CognitiveServices",
                "properties": {
                    "publicNetworkAccess": "Disabled"
                }
            },
            "api_version": "2021-10-01",
            "method": "PUT"
        },
        # 3. Key Vault
        {
            "type": "Key Vault",
            "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.KeyVault/vaults/kv-{resource_name}",
            "body": {
                "location": "eastus2",
                "properties": {
                    "sku": {
                        "family": "A",
                        "name": "standard"
                    },
                    "tenantId": "your-tenant-id", # Replace with your tenant ID or use os.environ.get
                    "accessPolicies": [],
                    "publicNetworkAccess": "Disabled"
                }
            },
            "api_version": "2021-11-01-preview",
            "method": "PUT"
        }
    ]
    data = {
        "project_name": project_name,
        "resource_ops": resource_ops
    }
    try:
        # Make POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Check if request was successful
        if response.status_code == 200 or response.status_code == 201:
            print("POST Request Successful!")
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

call_api_post()