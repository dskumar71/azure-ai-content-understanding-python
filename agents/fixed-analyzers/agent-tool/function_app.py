import azure.functions as func
import logging
import json
import os
from cu_client import AzureContentUnderstandingClient
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        file_url = req_body.get('file_url')
        schema = req_body.get('schema')
        analyzer_id = req_body.get('analyzer_id')

        if not file_url or not schema:
            return func.HttpResponse(
                "Invalid request body. 'file_url' and 'schema' are required.",
                status_code=400
            )

        # if not isinstance(schema, list):
        #     return func.HttpResponse(
        #         "'schema' should be a list of fields.",
        #         status_code=400
        #     )

        # for field in schema:
        #     if not all(k in field for k in ("name", "description", "type", "method")):
        #         return func.HttpResponse(
        #             "Each field in 'schema' must contain 'name', 'description', 'type', and 'method'.",
        #             status_code=400
        #         )
        #     if field['type'] == 'table' and 'subfields' in field:
        #         for subfield in field['subfields']:
        #             if not all(k in subfield for k in ("name", "description", "type", "method")):
        #                 return func.HttpResponse(
        #                     "Each subfield in 'subfields' must contain 'name', 'description', 'type', and 'method'.",
        #                     status_code=400
        #                 )
    except ValueError:
        pass

    client = AzureContentUnderstandingClient(
        endpoint=os.getenv("AZURE_CU_ENDPOINT"),
        api_version=os.getenv("AZURE_CU_API_VERSION"),
        subscription_key=os.getenv("AZURE_CU_API_KEY"),
        token_provider=lambda: "your_token_here"
    )
    
    analyzer_cleanup = False
    if not client.check_if_analyzer_exists(analyzer_id=analyzer_id):
        analyzer_cleanup = True
        analyzer = client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            analyzer_template=schema
        )
        if analyzer.status_code != 201:
            return func.HttpResponse(
                "Analyzer creation failed.",
                status_code=500
            )
        # Wait for the analyzer to be created
        analyzer = client.poll_result(analyzer)
        
    resp = client.begin_analyze(analyzer_id=analyzer_id, file_location=file_url)
    output = client.poll_result(resp)
    if analyzer_cleanup == True:
        cleanup = client.delete_analyzer(analyzer_id)
        if cleanup.status_code != 204:
            return func.HttpResponse(
                "Analyzer deletion failed.",
                status_code=500
            )

    markdown = output["result"]["contents"][0]["markdown"]
    fields = output["result"]["contents"][0]["fields"]
    result = {
        "markdown": markdown,
        "fields": fields
    }

    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200
    )
