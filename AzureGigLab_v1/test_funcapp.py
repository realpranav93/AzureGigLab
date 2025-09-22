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
    project_name = "TestProjectAjay"
    # Request body
    resource_ops = [
        {
            "type": "Storage Account",
            "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{resource_name}",
            "body": {
                "sku": {"name": "Standard_LRS"},
                "kind": "StorageV2",
                "location": "eastus2"
            },
            "api_version": "2021-04-01",
            "method": "PUT"
        },
        {
            "type": "SQL Server",
            "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Sql/servers/{resource_name}",
            "body": {
                "location": "eastus2",
                "properties": {
                    "administratorLogin": "sqladminuser",
                    "administratorLoginPassword": "YourStrongP@ssw0rd!"
                }
            },
            "api_version": "2021-02-01-preview",
            "method": "PUT"
        },
        {
            "type": "AI Foundry",
            "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{resource_name}",
            "body": {
                "location": "eastus2",
                "sku": {"name": "S0"},
                "kind": "CognitiveServices",
                "properties": {
                    "customSubDomainName": f"cog{project_name.lower()}{random.randint(100,999)}"
                }
            },
            "api_version": "2021-04-30",
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