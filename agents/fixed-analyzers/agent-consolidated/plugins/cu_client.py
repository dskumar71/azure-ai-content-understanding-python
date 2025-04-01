import requests
from requests.models import Response
import logging
import json
import time
import random
from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class AzureContentUnderstandingClient:
    def __init__(
        self,
        endpoint: str = os.getenv("AZURE_CU_ENDPOINT"),
        api_version: str = os.getenv("AZURE_CU_API_VERSION"),
        subscription_key: str = os.getenv("AZURE_CU_API_KEY"),
        token_provider: callable = None,
        x_ms_useragent: str = "cu-sample-code",
    ):
        if not subscription_key and not token_provider:
            raise ValueError(
                "Either subscription key or token provider must be provided."
            )
        if not api_version:
            raise ValueError("API version must be provided.")
        if not endpoint:
            raise ValueError("Endpoint must be provided.")

        # Provide a default token provider if none is supplied
        if token_provider is None:
            token_provider=lambda: "your_token_here"

        self._endpoint = endpoint.rstrip("/")
        self._api_version = api_version
        self._logger = logging.getLogger(__name__)
        self._headers = self._get_headers(
            subscription_key, token_provider(), x_ms_useragent
        )

    def _get_analyzer_url(self, endpoint, api_version, analyzer_id):
        return f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}?api-version={api_version}"  # noqa

    def _get_analyzer_list_url(self, endpoint, api_version):
        return f"{endpoint}/contentunderstanding/analyzers?api-version={api_version}"

    def _get_analyze_url(self, endpoint, api_version, analyzer_id):
        return f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}:analyze?api-version={api_version}"  # noqa

    def _get_training_data_config(
        self, storage_container_sas_url, storage_container_path_prefix
    ):
        return {
            "containerUrl": storage_container_sas_url,
            "kind": "blob",
            "prefix": storage_container_path_prefix,
        }

    def _get_headers(self, subscription_key, api_token, x_ms_useragent):
        """Returns the headers for the HTTP requests.
        Args:
            subscription_key (str): The subscription key for the service.
            api_token (str): The API token for the service.
            enable_face_identification (bool): A flag to enable face identification.
        Returns:
            dict: A dictionary containing the headers for the HTTP requests.
        """
        headers = (
            {"Ocp-Apim-Subscription-Key": subscription_key}
            if subscription_key
            else {"Authorization": f"Bearer {api_token}"}
        )
        headers["x-ms-useragent"] = x_ms_useragent
        return headers

    def get_all_analyzers(self):
        """
        Retrieves a list of all available analyzers from the content understanding service.

        This method sends a GET request to the service endpoint to fetch the list of analyzers.
        It raises an HTTPError if the request fails.

        Returns:
            dict: A dictionary containing the JSON response from the service, which includes
                  the list of available analyzers.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        response = requests.get(
            url=self._get_analyzer_list_url(self._endpoint, self._api_version),
            headers=self._headers,
        )
        response.raise_for_status()
        return response.json()
    
    def check_if_analyzer_exists(self, analyzer_id: str):
        """
        Checks if an analyzer with the given ID exists in the content understanding service.

        Args:
            analyzer_id (str): The unique identifier for the analyzer.

        Returns:
            bool: True if the analyzer exists, False otherwise.
        """
        
        response = requests.get(
            url=self._get_analyzer_url(self._endpoint, self._api_version, analyzer_id),
            headers=self._headers,
        )
        if response.status_code == 404:
            return False
        if response.status_code == 200:
            return True
        response.raise_for_status()
        return False
        
        

    def get_analyzer_detail_by_id(self, analyzer_id):
        """
        Retrieves a specific analyzer detail through analyzerid from the content understanding service.
        This method sends a GET request to the service endpoint to get the analyzer detail.

        Args:
            analyzer_id (str): The unique identifier for the analyzer.

        Returns:
            dict: A dictionary containing the JSON response from the service, which includes the target analyzer detail.

        Raises:
            HTTPError: If the request fails.
        """
        response = requests.get(
            url=self._get_analyzer_url(self._endpoint, self._api_version, analyzer_id),
            headers=self._headers,
        )
        response.raise_for_status()
        return response.json()

    def begin_create_analyzer(
        self,
        analyzer_id: str,
        analyzer_template: dict = None,
        analyzer_template_path: str = "",
        training_storage_container_sas_url: str = "",
        training_storage_container_path_prefix: str = "",
    ):
        """
        Initiates the creation of an analyzer with the given ID and schema.

        Args:
            analyzer_id (str): The unique identifier for the analyzer.
            analyzer_template (dict, optional): The schema definition for the analyzer. Defaults to None.
            analyzer_template_path (str, optional): The file path to the analyzer schema JSON file. Defaults to "".
            training_storage_container_sas_url (str, optional): The SAS URL for the training storage container. Defaults to "".
            training_storage_container_path_prefix (str, optional): The path prefix within the training storage container. Defaults to "".

        Raises:
            ValueError: If neither `analyzer_template` nor `analyzer_template_path` is provided.
            requests.exceptions.HTTPError: If the HTTP request to create the analyzer fails.

        Returns:
            requests.Response: The response object from the HTTP request.
        """
        if analyzer_template_path and Path(analyzer_template_path).exists():
            with open(analyzer_template_path, "r") as file:
                analyzer_template = json.load(file)

        if not analyzer_template:
            raise ValueError("Analyzer schema must be provided.")

        if (
            training_storage_container_sas_url
            and training_storage_container_path_prefix
        ):  # noqa
            analyzer_template["trainingData"] = self._get_training_data_config(
                training_storage_container_sas_url,
                training_storage_container_path_prefix,
            )

        headers = {"Content-Type": "application/json"}
        headers.update(self._headers)

        response = requests.put(
            url=self._get_analyzer_url(self._endpoint, self._api_version, analyzer_id),
            headers=headers,
            json=analyzer_template,
        )
        response.raise_for_status()
        self._logger.info(f"Analyzer {analyzer_id} create request accepted.")
        return response

    def delete_analyzer(self, analyzer_id: str):
        """
        Deletes an analyzer with the specified analyzer ID.

        Args:
            analyzer_id (str): The ID of the analyzer to be deleted.

        Returns:
            response: The response object from the delete request.

        Raises:
            HTTPError: If the delete request fails.
        """
        response = requests.delete(
            url=self._get_analyzer_url(self._endpoint, self._api_version, analyzer_id),
            headers=self._headers,
        )
        response.raise_for_status()
        self._logger.info(f"Analyzer {analyzer_id} deleted.")
        return response

    def _retry_with_backoff(self, func, *args, max_retries=5, **kwargs):
        """
        Helper method to retry a function with exponential backoff.

        Args:
            func (callable): The function to retry.
            *args: Positional arguments to pass to the function.
            max_retries (int): Maximum number of retries.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Any: The result of the function call if successful.

        Raises:
            Exception: The last exception raised if all retries fail.
        """
        delay = 1  # Initial delay in seconds
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    self._logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    delay += random.uniform(0, 1)  # Add jitter to avoid thundering herd
                else:
                    self._logger.error(f"All {max_retries} attempts failed. Raising exception.")
                    raise

    def begin_analyze(self, analyzer_id: str, file_location: str):
        """
        Begins the analysis of a file or URL using the specified analyzer with retry logic.

        Args:
            analyzer_id (str): The ID of the analyzer to use.
            file_location (str): The path to the file or the URL to analyze.

        Returns:
            Response: The response from the analysis request.

        Raises:
            ValueError: If the file location is not a valid path or URL.
            HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        def analyze_request():
            data = None
            if Path(file_location).exists():
                with open(file_location, "rb") as file:
                    data = file.read()
                headers = {"Content-Type": "application/octet-stream"}
            elif "https://" in file_location or "http://" in file_location:
                data = {"url": file_location}
                headers = {"Content-Type": "application/json"}
            else:
                raise ValueError("File location must be a valid path or URL.")

            headers.update(self._headers)
            if isinstance(data, dict):
                response = requests.post(
                    url=self._get_analyze_url(
                        self._endpoint, self._api_version, analyzer_id
                    ),
                    headers=headers,
                    json=data,
                )
            else:
                response = requests.post(
                    url=self._get_analyze_url(
                        self._endpoint, self._api_version, analyzer_id
                    ),
                    headers=headers,
                    data=data,
                )

            response.raise_for_status()
            self._logger.info(
                f"Analyzing file {file_location} with analyzer: {analyzer_id}"
            )
            return response

        return self._retry_with_backoff(analyze_request)

    def get_image_from_analyze_operation(
        self, analyze_response: Response, image_id: str
    ):
        """Retrieves an image from the analyze operation using the image ID.
        Args:
            analyze_response (Response): The response object from the analyze operation.
            image_id (str): The ID of the image to retrieve.
        Returns:
            bytes: The image content as a byte string.
        """
        operation_location = analyze_response.headers.get("operation-location", "")
        if not operation_location:
            raise ValueError(
                "Operation location not found in the analyzer response header."
            )
        operation_location = operation_location.split("?api-version")[0]
        image_retrieval_url = (
            f"{operation_location}/images/{image_id}?api-version={self._api_version}"
        )
        try:
            response = requests.get(url=image_retrieval_url, headers=self._headers)
            response.raise_for_status()

            assert response.headers.get("Content-Type") == "image/jpeg"

            return response.content
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed: {e}")
            return None

    def poll_result(
        self,
        response: Response,
        timeout_seconds: int = 120,
        polling_interval_seconds: int = 2,
    ):
        """
        Polls the result of an asynchronous operation until it completes or times out.

        Args:
            response (Response): The initial response object containing the operation location.
            timeout_seconds (int, optional): The maximum number of seconds to wait for the operation to complete. Defaults to 120.
            polling_interval_seconds (int, optional): The number of seconds to wait between polling attempts. Defaults to 2.

        Raises:
            ValueError: If the operation location is not found in the response headers.
            TimeoutError: If the operation does not complete within the specified timeout.
            RuntimeError: If the operation fails.

        Returns:
            dict: The JSON response of the completed operation if it succeeds.
        """
        operation_location = response.headers.get("operation-location", "")
        if not operation_location:
            raise ValueError("Operation location not found in response headers.")

        headers = {"Content-Type": "application/json"}
        headers.update(self._headers)

        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                raise TimeoutError(
                    f"Operation timed out after {timeout_seconds:.2f} seconds."
                )

            response = requests.get(operation_location, headers=self._headers)
            response.raise_for_status()
            status = response.json().get("status").lower()
            if status == "succeeded":
                self._logger.info(
                    f"Request result is ready after {elapsed_time:.2f} seconds."
                )
                return response.json()
            elif status == "failed":
                self._logger.error(f"Request failed. Reason: {response.json()}")
                raise RuntimeError("Request failed.")
            else:
                self._logger.info(
                    f"Request {operation_location.split('/')[-1].split('?')[0]} in progress ..."
                )
            time.sleep(polling_interval_seconds)

    def process_files_in_parallel(self, analyzer_id: str, file_urls: list) -> dict:
        """
        Processes multiple files in parallel using the specified analyzer.

        Args:
            analyzer_id (str): The ID of the analyzer to use.
            file_urls (list): A list of file URLs to process.

        Returns:
            dict: A dictionary containing the results for each file.
        """
        def process_file(file_url):
            try:
                response = self.begin_analyze(analyzer_id, file_url)
                result = self.poll_result(response)
                return {
                    "file_url": file_url,
                    "result": result
                }
            except Exception as e:
                return {
                    "file_url": file_url,
                    "error": str(e)
                }

        results = {}
        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(process_file, file_url): file_url for file_url in file_urls}
            for future in as_completed(future_to_file):
                file_url = future_to_file[future]
                try:
                    result = future.result()
                    if "error" in result:
                        self._logger.error(f"Error processing file {file_url}: {result['error']}")
                    else:
                        results[file_url] = result["result"]
                except Exception as e:
                    self._logger.error(f"Exception processing file {file_url}: {e}")

        return results

    def run_cu(self, file_urls, analyzer_id, analyzer_schema) -> dict:
        """
        Processes files using the specified analyzer and schema.

        Args:
            file_urls (list or str): A list of file URLs or a single file URL to process.
            analyzer_id (str): The ID of the analyzer to use.
            analyzer_schema_file (str): Path to the analyzer schema file.

        Returns:
            dict: A dictionary containing the results for each file.
        """
        self._logger.info('Starting run_cu processing.')

        # Initialize analyzer_cleanup to False
        analyzer_cleanup = False

        # Check if the analyzer exists, if not create it
        if not self.check_if_analyzer_exists(analyzer_id=analyzer_id):
            analyzer = self.begin_create_analyzer(
                analyzer_id=analyzer_id,
                analyzer_template=analyzer_schema
            )
            if analyzer.status_code != 201:
                self._logger.error(f"Analyzer creation failed. Status code: {analyzer.status_code}")
                return {
                    "error": f"Analyzer creation failed."
                }
            else:
                self._logger.info(f"Analyzer {analyzer_id} creation request accepted.")

            analyzer = self.poll_result(analyzer)
            if analyzer["status"].lower() != "succeeded":
                self._logger.error(f"Analyzer creation failed. Status: {analyzer['status']}")
                return {
                    "error": f"Analyzer creation failed."
                }
            else:
                analyzer_cleanup = True
                self._logger.info(f"Analyzer {analyzer_id} created successfully.")

        if isinstance(file_urls, str):
            file_urls = [file_urls]
        elif not isinstance(file_urls, list):
            return {
                "error": "file_urls should be a list or a string."
            }

        # Use the parallel processing method
        file_outputs = self.process_files_in_parallel(analyzer_id, file_urls)

        # Cleanup the analyzer if it was created in this run
        if analyzer_cleanup == True:
            cleanup = self.delete_analyzer(analyzer_id)
            if cleanup.status_code != 204:
                self._logger.error(f"Analyzer deletion failed. Status code: {cleanup.status_code}")
                return {
                    "error": f"Analyzer deletion failed."
                }
            else:
                self._logger.info(f"Analyzer {analyzer_id} deleted successfully.")

        return file_outputs
