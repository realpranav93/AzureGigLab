import azure.functions as func
import json
import logging
import storage_helper

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="create-storage")
def create_storage(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to create a storage account.")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON format.", status_code=400)

    # Basic validation
    required_keys = ["storage_account_name", "resource_group", "location"]
    if not all(key in req_body for key in required_keys):
        return func.HttpResponse(
            f"Please provide all required fields: {', '.join(required_keys)}",
            status_code=400
        )

    result = storage_helper.create_storage_account(req_body)

    if result["success"]:
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=500
        )
