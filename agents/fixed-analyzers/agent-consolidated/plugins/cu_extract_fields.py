import json, os
import aiohttp
import logging
import json
import os
from plugins.cu_client import AzureContentUnderstandingClient
from dotenv import find_dotenv, load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            analyzer = client.begin_create_analyzer(
                analyzer_id=analyzer_id,
                analyzer_template=analyzer_schema_file
            )
            if analyzer.status_code != 201:
                return {
                    "error": f"Analyzer creation failed."
                }

            analyzer = client.poll_result(analyzer)

        if isinstance(file_urls, str):
            file_urls = [file_urls]
        elif not isinstance(file_urls, list):
            return {
                "error": "file_urls should be a list or a string."
            }

        def process_file(file_url):
            if not file_url.startswith("http"):
                return {
                    "error": f"Invalid file URL: {file_url}"
                }
            resp = client.begin_analyze(analyzer_id=analyzer_id, file_location=file_url)
            output = client.poll_result(resp)

            markdown = output["result"]["contents"][0]["markdown"]
            fields = output["result"]["contents"][0]["fields"]
            return {
                "file_url": file_url,
                "result": {
                    "markdown": markdown,
                    "fields": fields
                }
            }

        file_outputs = {}
        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(process_file, file_url): file_url for file_url in file_urls}
            for future in as_completed(future_to_file):
                file_url = future_to_file[future]
                try:
                    result = future.result()
                    if "error" in result:
                        logging.error(f"Error processing file {file_url}: {result['error']}")
                    else:
                        file_outputs[file_url] = result["result"]
                except Exception as e:
                    logging.error(f"Exception processing file {file_url}: {e}")

        if analyzer_cleanup:
            cleanup = client.delete_analyzer(analyzer_id)
            if cleanup.status_code != 204:
                return {
                    "error": f"Analyzer deletion failed."
                }

        return file_outputs
