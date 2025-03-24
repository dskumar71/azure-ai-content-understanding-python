import json, os
import aiohttp
import logging
import json
import os
from plugins.cu_client import AzureContentUnderstandingClient
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

class cu_extract_fields:
    def run_cu(self, file_url, analyzer_id, analyzer_schema_file) -> dict:
        logging.info('Starting run_cu processing.')

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
                analyzer_template=analyzer_schema_file
            )
            if analyzer.status_code != 201:
                return {
                    "error": f"Analyzer creation failed."
                }
                
            # Wait for the analyzer to be created
            analyzer = client.poll_result(analyzer)
            
        resp = client.begin_analyze(analyzer_id=analyzer_id, file_location=file_url)
        output = client.poll_result(resp)
        if analyzer_cleanup == True:
            cleanup = client.delete_analyzer(analyzer_id)
            if cleanup.status_code != 204:
                return {
                    "error": f"Analyzer deletion failed."
                }

        markdown = output["result"]["contents"][0]["markdown"]
        fields = output["result"]["contents"][0]["fields"]
        result = {
            "markdown": markdown,
            "fields": fields
        }

        if "fields" not in result:
            print(f"Unexpected API response: {output}")
            return {
                "error": "Unexpected API response format",
                "response": str(output)
            }
    
        company_name = fields.get("CompanyName", {})
        company_address = fields.get("CompanyAddress", {})
        
        return {
            "CompanyName": company_name.get("valueString", "Unknown"),
            "CompanyAddress": company_address.get("valueString", "Unknown"),
            "FullResponse": result  # Include full response for debugging
        }
