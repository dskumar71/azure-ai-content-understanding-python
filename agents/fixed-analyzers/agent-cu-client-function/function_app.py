import azure.functions as func
import logging
import json
import os
from dotenv import find_dotenv, load_dotenv
from cu_client import AzureContentUnderstandingClient

load_dotenv(find_dotenv())

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    client = AzureContentUnderstandingClient(
        endpoint=os.getenv("AZURE_CU_ENDPOINT"),
        api_version=os.getenv("AZURE_CU_API_VERSION"),
        subscription_key=os.getenv("AZURE_CU_API_KEY"),
        token_provider=lambda: "your_token_here"
    )
    
    try:
        req_body = req.get_json()
        file_urls = req_body.get('file_urls')
        analyzer_id = req_body.get('analyzer_id')
        analyzer_schema = req_body.get('analyzer_schema')
        logging.info(f"req_body: {req_body}")
        
        if not file_urls or not analyzer_schema or not analyzer_id:
            logging.error("Invalid request body. 'file_urls', 'analyzer_id' and 'analyzer_schema' are required.")
            return func.HttpResponse(
                json.dumps({"error": "Invalid request body. 'file_urls', 'analyzer_id' and 'analyzer_schema' are required."}),
                mimetype="application/json",
                status_code=400
            )

        if isinstance(file_urls, str):
            file_urls = [file_urls]
        elif isinstance(file_urls, dict):
            file_urls = list(file_urls.values())
        elif not isinstance(file_urls, list):
            logging.error("file_urls should be a list or a string.")
            return func.HttpResponse(
                json.dumps({"error": "file_urls should be a list or a string."}),
                mimetype="application/json",
                status_code=400
            )

    except ValueError:
        logging.error(result)
        return func.HttpResponse(
                json.dumps(result),
                mimetype="application/json",
                status_code=400
            )
    
    result = client.run_cu(file_urls, analyzer_id, analyzer_schema)
    logging.info(f"Result: {result}")
    
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200
    )
