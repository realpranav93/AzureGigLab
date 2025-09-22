from openai import AzureOpenAI, azure_ad_token_provider
import requests
import json
import os
import random
import string

# Azure Function App URL
FUNCTION_APP_URL = "http://localhost:7071/api/CreateAzureResource"

# def get_random_string(length=8):
#     """Generate a random string of fixed length."""
#     letters = string.ascii_lowercase
#     return ''.join(random.choice(letters) for i in range(length))


def get_llm_response(prompt):
    deployment = "gpt-5-mini"

    endpoint = "https://azureoaiexpt.openai.azure.com/"
    client = AzureOpenAI(azure_endpoint=endpoint,
                         api_key="4c8dLceQrsg69gjT0iD6m7y4VUhWdJJJMOEeuAm8RGihiGTcvIVVJQQJ99BEACYeBjFXJ3w3AAABACOGHkiw",
                         api_version="2024-12-01-preview")
    try:
        completion = client.chat.completions.create(model=deployment,
                                                    messages=[
                                                        {
                                                            "role": "user",
                                                            "content": prompt
                                                    }]
                                                )

        choice = completion.choices[0].message.content.strip().lower()
        return choice
    except Exception as e:
        print(f"Error getting LLM confirmation: {e}")
        return False


def azure_resources(resource_ops, project_name):
    """Create Azure resources by calling the Azure Function."""
    flag_rg = None
    subscription_id = "21877728-764b-495a-baac-fd6cea808148"
    location = "eastus2"
   
    r_method = "PUT"
    api_version = "2021-04-01"
    prompt_rg = f"Here is a project name: {project_name}. Create a resource group name with a syntax 'rg-<name>'. <name> should be name of the project. Return the resource group name as output"
    resource_group_name = get_llm_response(prompt_rg)
    resource_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourcegroups/{resource_group_name}"

    payload = {
            "url": resource_url,
            "body": {"location": location},
            "api_version": api_version,
            "method": r_method
        }
    try:
        response = requests.post(FUNCTION_APP_URL, json=payload)
        if response.status_code >= 200 and response.status_code < 300:
            print(f"Successfully initiated creation of {resource_group_name}. Status: {response.status_code}")
            print(response.text)
            flag_rg = True
        else:
            print(f"Failed to create {resource_group_name}. Status: {response.status_code}")
            print(response.text)
            flag_rg = False
    except requests.exceptions.RequestException as e:
        print(f"Error calling Azure Function for {resource_group_name}: {e}")
    print("-" * 20)

    if flag_rg:
        # base_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"

        for resource in resource_ops:
            if resource['method'] == 'PUT':
                resource_type = resource['type']
                url = resource['url'].replace('{resource_group}', resource_group_name).replace('{subscription_id}', subscription_id)
                r_body = resource['body']
                r_method = resource['method']
                api_version = resource['api_version']

                resource_type_string = resource_type.split(' ')[0].lower()
                prompt_rg = f"Here is a project: {project_name}. Create a name for {resource_type} with a syntax '{resource_type_string}<name>'. <name> should be name of the project. Return the resource name as output."
                resource_name = get_llm_response(prompt_rg)
                url = url.replace('{resource_name}', resource_name)
                resource_url = url
                print("Resource URL:", resource_url)
                payload = {
                    "url": resource_url,
                    "body": r_body,
                    "api_version": api_version,
                    "method": r_method
                }
                try:
                    response = requests.post(FUNCTION_APP_URL, json=payload)
                    if response.status_code >= 200 and response.status_code < 300:
                        print(f"Successfully initiated creation of {resource_name}. Status: {response.status_code}")
                        print(response.text)
                    else:
                        print(f"Failed to create {resource_name}. Status: {response.status_code}")
                        print(response.text)
                except requests.exceptions.RequestException as e:
                    print(f"Error calling Azure Function for {resource_name}: {e}")
                print("-" * 20)

            elif resource['method'] == 'DELETE':
                resource_type = resource['type']
                url = resource['url'].replace('{resource_group}', resource_group_name).replace('{subscription_id}', subscription_id)
                resource_name = url.split('/')[-1]
                r_body = resource['body']
                r_method = resource['method']
                api_version = resource['api_version']

                resource_url = url
                print("Resource URL:", resource_url)
                payload = {
                    "url": resource_url,
                    "body": r_body,
                    "api_version": api_version,
                    "method": r_method
                }
                try:
                    response = requests.post(FUNCTION_APP_URL, json=payload)
                    if response.status_code >= 200 and response.status_code < 300:
                        print(f"Successfully initiated deletion of {resource_name}. Status: {response.status_code}")
                        print(response.text)
                    else:
                        print(f"Failed to delete {resource_name}. Status: {response.status_code}")
                        print(response.text)
                except requests.exceptions.RequestException as e:
                    print(f"Error calling Azure Function for {resource_name}: {e}")
                print("-" * 20)
    else:
        print("Something went wrong while creating the resources.")


    # 1. Create Resource Group
    # resource_group_payload = {
    #     "url": f"https://management.azure.com/subscriptions/{subscription_id}/resourcegroups/{resource_group}",
    #     "body": {"location": location},
    #     "api_version": "2021-04-01",
    #     "method": "PUT"
    # }

    # # 2. Create Storage Accountc
    # # storage_account_name = f"storage{get_random_string()}"
    # storage_account_payload = {
    #     "url": f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}",
    #     "body": {
    #         "sku": {"name": "Standard_LRS"},
    #         "kind": "StorageV2",
    #         "location": location
    #     },
    #     "api_version": "2021-04-01",
    #     "method": "PUT"
    # }

    # # 3. Create App Service Plan
    # # app_service_plan_name = f"plan-{get_random_string()}"
    # app_service_plan_payload = {
    #     "url": f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/serverfarms/{app_service_plan_name}",
    #     "body": {
    #         "sku": {"name": "B1", "tier": "Basic", "size": "B1", "family": "B", "capacity": 1},
    #         "kind": "linux",
    #         "location": location,
    #         "properties": {"reserved": True} # For Linux
    #     },
    #     "api_version": "2021-02-01",
    #     "method": "PUT"
    # }
    
    # # 4. Create App Service
    # # app_service_name = f"app-{get_random_string()}"
    # app_service_payload = {
    #     "url": f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{app_service_name}",
    #     "body": {
    #         "location": location,
    #         "properties": {
    #             "serverFarmId": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/serverfarms/{app_service_plan_name}"
    #         }
    #     },
    #     "api_version": "2021-02-01",
    #     "method": "PUT"
    # }

    # azure_resources = [
    #     resource_group_payload,
    #     storage_account_payload,
    #     app_service_plan_payload,
    #     app_service_payload
    # ]

    # for resource in azure_resources:
    #     resource_name = resource['url'].split('/')[-1]
    #     prompt = f"Create Azure resource '{resource_name}' with the following details: {json.dumps(resource['body'])}"
        
    #     print(f"Seeking LLM confirmation for: {resource_name}")
    #     if get_llm_confirmation(prompt):
    #         print(f"LLM approved. Creating {resource_name}...")
    #         try:
    #             response = requests.post(FUNCTION_APP_URL, json=resource)
    #             if response.status_code >= 200 and response.status_code < 300:
    #                 print(f"Successfully initiated creation of {resource_name}. Status: {response.status_code}")
    #                 print(response.text)
    #             else:
    #                 print(f"Failed to create {resource_name}. Status: {response.status_code}")
    #                 print(response.text)
    #         except requests.exceptions.RequestException as e:
    #             print(f"Error calling Azure Function for {resource_name}: {e}")
    #     else:
    #         print(f"LLM denied the creation of {resource_name}.")
        
    #     print("-" * 20)

# if __name__ == "__main__":
    # Ensure you have set the following environment variables:
    # OPENAI_API_KEY, SUBSCRIPTION_ID, TENANT_ID, CLIENT_ID, CLIENT_SECRET
    # Also, make sure your Azure Function App is running locally.
    
    # """
    # project_name = "myhackproject2025"
    # # Please include url, body, api_version, method in each resource operation. Create a storage account, sql server and Azure AI foundry
    # resource_ops = [
    #     {
    #         "type": "Storage Account",
    #         "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{resource_name}",
    #         "body": {
    #             "sku": {"name": "Standard_LRS"},
    #             "kind": "StorageV2",
    #             "location": "eastus2"
    #         },
    #         "api_version": "2021-04-01",
    #         "method": "PUT"
    #     },
    #     {
    #         "type": "SQL Server",
    #         "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Sql/servers/{resource_name}",
    #         "body": {
    #             "location": "eastus2",
    #             "properties": {
    #                 "administratorLogin": "sqladminuser",
    #                 "administratorLoginPassword": "YourStrongP@ssw0rd!"
    #             }
    #         },
    #         "api_version": "2021-02-01-preview",
    #         "method": "PUT"
    #     },
    #     {
    #         "type": "AI Foundry",
    #         "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{resource_name}",
    #         "body": {
    #             "location": "eastus2",
    #             "sku": {"name": "S0"},
    #             "kind": "CognitiveServices",
    #             "properties": {
    #                 "customSubDomainName": f"cog{project_name.lower()}{random.randint(100,999)}"
    #             }
    #         },
    #         "api_version": "2021-04-30",
    #         "method": "PUT"
    #     }
    # ]

    # # Create resource ops for deletion of the AI Foundry service
    # resource_ops_d = [
    #     {
    #         "type": "AI Foundry Deletion",
    #         "url": "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/aihack2025",
    #         "body": {},
    #         "api_version": "2021-04-30",
    #         "method": "DELETE"
    #     }
    # ]
    
    # azure_resources(resource_ops_d, project_name=project_name)
