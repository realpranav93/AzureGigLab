import azure.functions as func
import logging
import os
import json
import requests
from openai import AzureOpenAI
from msal import ConfidentialClientApplication


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


# def azure_resources(resource_ops, project_name):
#     """Create Azure resources by calling the Azure Function."""
    

def send_request(req_data):
    """Sends a request to the Azure Management API."""
    
    # Create a mock response class for error handling
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

    try:
        resource_creation_url = req_data.get('url')
        resource_creation_body = req_data.get('body')
        api_version = req_data.get('api_version', '2021-04-01')
        method = req_data.get('method', 'PUT').upper()
    except AttributeError:
        return MockResponse("Invalid request data.", 400)
        
    if not resource_creation_url or not resource_creation_body:
        return MockResponse("Please pass 'url' and 'body' in the request body.", 400)

    try:
        tenant_id = os.environ["AZURE_TENANT_ID"]
        client_id = os.environ["AZURE_CLIENT_ID"]
        client_secret = os.environ["AZURE_CLIENT_SECRET"]

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        scope = ["https://management.azure.com/.default"]

        msal_app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
        result = msal_app.acquire_token_for_client(scopes=scope)

        if "access_token" in result:
            access_token = result['access_token']
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url_with_api_version = f"{resource_creation_url}?api-version={api_version}"

            if method == 'PUT':
                response = requests.put(url_with_api_version, headers=headers, data=json.dumps(resource_creation_body))
            elif method == 'POST':
                response = requests.post(url_with_api_version, headers=headers, data=json.dumps(resource_creation_body))
            elif method == 'DELETE':
                response = requests.delete(url_with_api_version, headers=headers)
            else:
                return MockResponse(f"Unsupported HTTP method: {method}", 405)
            
            return response

        else:
            error_description = result.get('error_description', 'Unknown error')
            logging.error(f"Failed to acquire token: {error_description}")
            return MockResponse("Failed to acquire authentication token.", 500)

    except Exception as e:
        logging.error(f"An error occurred in send_request: {e}")
        return MockResponse(f"An internal error occurred: {e}", 500)
    
app = func.FunctionApp()

@app.route(route="CreateAzureResource", auth_level=func.AuthLevel.ANONYMOUS)
def CreateAzureResource(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    msgs = ""
    # Create 2 variables. One which excepts resource_ops and other excepts project_name
    resource_ops = req.get_json().get('resource_ops', [])
    project_name = req.get_json().get('project_name', 'sampleprojecthack2025')

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
        response = send_request(payload)
        if response.status_code >= 200 and response.status_code < 300:
            msg = f"Successfully initiated creation of {resource_group_name}. Status: {response.status_code}"
            logging.info(msg)
            logging.info(response.text)
            flag_rg = True
        else:
            msg = f"Failed to create {resource_group_name}. Status: {response.status_code}"
            logging.error(msg)
            logging.error(response.text)
            flag_rg = False
        msgs += msg + "\n"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Azure Function for {resource_group_name}: {e}")
    logging.info("-" * 20)

    try:

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
                        response = send_request(payload)
                        if response.status_code >= 200 and response.status_code < 300:
                            msg = f"Successfully initiated creation of {resource_name}. Status: {response.status_code}"
                            logging.info(msg)
                            logging.info(response.text)
                        else:
                            msg = f"Failed to create {resource_name}. Status: {response.status_code}"
                            logging.error(msg)
                            logging.error(response.text)
                        msgs += msg + "\n"
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error calling Azure Function for {resource_name}: {e}")
                    logging.info("-" * 20)

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
                        response = send_request(payload)
                        if response.status_code >= 200 and response.status_code < 300:
                            msg = f"Successfully initiated deletion of {resource_name}. Status: {response.status_code}"
                            logging.info(msg)
                            logging.info(response.text)
                        else:
                            msg = f"Failed to delete {resource_name}. Status: {response.status_code}"
                            logging.warning(msg)
                            logging.warning(response.text)
                        msgs += msg + "\n"
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error calling Azure Function for {resource_name}: {e}")
                    logging.info("-" * 20)
        else:
            logging.error("Something went wrong while creating the resources.")
        final_msg = "Resource operations completed successfully. \n" + msgs
        return func.HttpResponse(final_msg, status_code=200)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return func.HttpResponse(f"An error occurred: {e}", status_code=500)