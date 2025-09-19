import os
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient

def create_storage_account(config: dict):
    """
    Creates an Azure Storage Account based on the provided configuration.
    """
    try:
        # --- 1. Authentication ---
        credential = ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

        # --- 2. Initialize Clients ---
        resource_client = ResourceManagementClient(credential, subscription_id)
        storage_client = StorageManagementClient(credential, subscription_id)

        # --- 3. Ensure Resource Group ---
        rg_name = config["resource_group"]
        location = config["location"]
        resource_client.resource_groups.create_or_update(rg_name, {"location": location})

        # --- 4. Create Storage Account ---
        account_name = config["storage_account_name"]
        logging.info(f"Initiating creation of storage account '{account_name}' in '{rg_name}'.")

        poller = storage_client.storage_accounts.begin_create(
            rg_name,
            account_name,
            {
                "sku": {"name": config.get("sku", "Standard_LRS")},
                "kind": "StorageV2",
                "location": location,
            },
        )
        result = poller.result()
        logging.info(f"Successfully created storage account '{result.name}'.")
        
        return {"success": True, "name": result.name, "location": result.location}

    except KeyError as e:
        logging.error(f"Missing required environment variable or config key: {e}")
        return {"success": False, "error": f"Missing configuration: {e}"}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"success": False, "error": str(e)}
