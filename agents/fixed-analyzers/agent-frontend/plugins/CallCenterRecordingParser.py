import json, os
import aiohttp
from semantic_kernel.functions import kernel_function
import json

class CallCenterRecordingParserPlugin:
    """This is a plugin to parse and extract information from call recording audio files which can be passed as a list of URLs and extracts relevant pre-defined fields from it. Field results from the plugin should always be presented. Also produces a markdown representation of the audio transcript as WEBVTT for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    async def CallCenterRecordingParserPlugin(self, file_urls):
        print("\nRunning CallCenterRecordingParserPlugin")
        print(json.dumps(file_urls, indent=2))
        analyzer_id = 'callcenter-analyzer-agent-sample'
        analyzer_schema_file='../../../analyzer_templates/call_recording_analytics.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.load(f)
        url = os.getenv("CU_PLUGIN_URL")
        request_body = json.dumps({
            "analyzer_id": analyzer_id,
            "file_urls": file_urls,
            "analyzer_schema": analyzer_schema
        })
        headers = {
            "Content-Type": "application/json"
        }
        print(f"Request body: {request_body}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=request_body) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"API request failed with status {response.status}: {error_text}")
                        return {
                            "error": f"API request failed with status {response.status}",
                            "details": error_text
                        }
                    
                    response_json = await response.json()
                    
                    if "fields" not in response_json:
                        print(f"Unexpected API response: {response_json}")
                        return {
                            "error": "Unexpected API response format",
                            "response": str(response_json)
                        }
                    
                return response
            
            except Exception as e:
                print(f"Error calling cu client API: {str(e)}")
                return {
                    "error": f"Error processing: {str(e)}"
                }
