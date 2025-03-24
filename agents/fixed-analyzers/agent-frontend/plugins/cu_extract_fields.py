import json, os
import aiohttp

class cu_extract_fields: 
    async def extract_fields(self, file_url, actual_analyzer_id, analyzer_schema_file) -> dict:
        async with aiohttp.ClientSession() as session:
            with open(analyzer_schema_file, "r") as f:
                actual_analyzer_schema = json.loads(f.read())

            template = """
            {
              "analyzer_id":"${analyzer_id}",
              "file_url": "${file_url}",
              "schema": ${analyzer_schema}
            }
            """

            # Handle file_url being passed as a dictionary with a url property
            actual_url = file_url
            if isinstance(file_url, dict) and 'url' in file_url:
                actual_url = file_url['url']
            
            # Replace the analyzer_id placeholder with the actual analyzer ID
            template = template.replace("${analyzer_id}", actual_analyzer_id)
            # Replace the file_url placeholder with the actual file_url
            template = template.replace("${file_url}", actual_url)
            # Replace the analyzer_schema placeholder with the actual schema
            template = template.replace("${analyzer_schema}", json.dumps(actual_analyzer_schema))

            # Convert the template string to a JSON object
            payload = json.loads(template)
            
            url = os.getenv("CU_PLUGIN_URL")
            
            try:
                async with session.post(url, json=payload) as response:
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
                    
                    company_name = response_json["fields"].get("CompanyName", {})
                    company_address = response_json["fields"].get("CompanyAddress", {})
                    
                    return {
                        "CompanyName": company_name.get("valueString", "Unknown"),
                        "CompanyAddress": company_address.get("valueString", "Unknown"),
                        "FullResponse": response_json  # Include full response for debugging
                    }
            except Exception as e:
                print(f"Error calling document analysis API: {str(e)}")
                return {
                    "error": f"Error processing document: {str(e)}"
                }