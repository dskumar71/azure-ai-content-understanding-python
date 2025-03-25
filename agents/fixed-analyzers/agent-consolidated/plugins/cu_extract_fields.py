import json, os
import aiohttp
import logging
import json
import os
from plugins.cu_client import AzureContentUnderstandingClient
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

class cu_extract_fields:
    def run_cu(self, file_urls, analyzer_id, analyzer_schema_file) -> dict:
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

        # Convert file_urls to a list if it's not already
        if isinstance(file_urls, str):
            file_urls = [file_urls]
        elif not isinstance(file_urls, list):
            return {
                "error": "file_urls should be a list or a string."
            }
        file_outputs = {}
        for file_url in file_urls:
            print(f"\nProcessing file: {file_url}")
            if not file_url.startswith("http"):
                return {
                    "error": f"Invalid file URL: {file_url}"
                }    
            resp = client.begin_analyze(analyzer_id=analyzer_id, file_location=file_url)
            output = client.poll_result(resp)

            markdown = output["result"]["contents"][0]["markdown"]
            fields = output["result"]["contents"][0]["fields"]
            result = {
                # "filename": file_url.split("/")[-1],
                "markdown": markdown,
                "fields": fields
            }
            if "fields" not in result:
                print(f"Unexpected API response: {output}")
                return {
                    "error": "Unexpected API response format",
                    "response": str(output)
                }
            else:
                # print(f"Result: {result}")
                file_outputs[file_url] = result
        
            print(f"File outputs: {file_outputs}")

        if analyzer_cleanup == True:
            cleanup = client.delete_analyzer(analyzer_id)
            if cleanup.status_code != 204:
                return {
                    "error": f"Analyzer deletion failed."
                }

        return file_outputs
