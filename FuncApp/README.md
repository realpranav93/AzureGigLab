# Minimalist Azure Storage Account Creator

This Azure Function creates an Azure Storage Account using an HTTP trigger and a Service Principal for authentication.

## Project Structure
```
- FuncApp/
  - function_app.py       # HTTP trigger endpoint
  - storage_helper.py     # Logic for creating the storage account
  - host.json             # Function host configuration
  - local.settings.json   # Local environment settings
  - requirements.txt      # Python dependencies
```

---

## Execution Steps

### 1. Prerequisites
- Python 3.8+
- Azure Functions Core Tools
- Azure CLI

### 2. Setup Service Principal
Create a Service Principal with `Contributor` role on your subscription. This will be used by the function to authenticate.

```bash
az login
az ad sp create-for-rbac --name "StorageCreatorSP" --role "Contributor" --sdk-auth
```
This command will output a JSON object. Copy the `clientId`, `clientSecret`, and `tenantId`.

### 3. Configure Local Settings
Open `local.settings.json` and fill in the values from the previous step, along with your Azure Subscription ID.

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_SUBSCRIPTION_ID": "your-subscription-id",
    "AZURE_TENANT_ID": "your-tenant-id",
    "AZURE_CLIENT_ID": "your-client-id",
    "AZURE_CLIENT_SECRET": "your-client-secret"
  }
}
```

### 4. Install Dependencies
Navigate to the `FuncApp` directory and install the required Python packages.

```bash
cd FuncApp
pip install -r requirements.txt
```

### 5. Run the Function App
Start the local Functions host.

```bash
func start
```
The function will be available at `http://localhost:7071/api/create-storage`.

### 6. Create a Storage Account
Send a POST request to the function's endpoint with the required metadata. You can use `curl` or any REST client.

**Example using `curl`:**
Replace `your-unique-name` with a globally unique, lowercase, alphanumeric name for the storage account.

```bash
curl -X POST http://localhost:7071/api/create-storage \
-H "Content-Type: application/json" \
-d '{
    "storage_account_name": "your-unique-name123",
    "resource_group": "my-test-rg",
    "location": "eastus"
}'
```

#### **Successful Response (200 OK):**
```json
{
    "success": true,
    "name": "your-unique-name123",
    "location": "eastus"
}
```

#### **Error Response (500 Internal Server Error):**
```json
{
    "success": false,
    "error": "Details about the error..."
}
```

The function will first ensure the resource group exists (or create it), then proceed to create the storage account. The process is synchronous and will wait for the creation to complete.
