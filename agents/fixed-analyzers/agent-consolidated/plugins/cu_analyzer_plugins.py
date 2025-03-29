from semantic_kernel.functions import kernel_function
from plugins.cu_client import AzureContentUnderstandingClient
# from plugins.dynamic_schema_generator import generate_dynamic_field_schema

class TenKParserPlugin:
    """This is a plugin to parse annual financial reports also known as 10K files and extracts the relevant fields from the document. It should only be used for this type of file. Also produces a markdown representation of the document for adding to a vector store for RAG."""
    @kernel_function
    def TenKParserPlugin(self, file_urls):
        analyzer_id = 'financial-analyzer-agent-sample'
        analyzer_schema_file='../../../analyzer_templates/financial_report.json'
        client = AzureContentUnderstandingClient()
        result = client.run_cu(file_urls, analyzer_id, analyzer_schema_file)
        return result

class CallCenterRecordingParserPlugin:
    """This is a plugin to parse and extract information from call recording audio files and extracts relevant pre-defined fields from it. Also produces a markdown representation of the audio transcript as WEBVTT for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    def CallCenterRecordingParserPlugin(self, file_urls):
        analyzer_id = 'callcenter-analyzer-agent-sample'
        analyzer_schema_file='../../../analyzer_templates/call_recording_analytics.json'
        client = AzureContentUnderstandingClient()
        result = client.run_cu(file_urls, analyzer_id, analyzer_schema_file)
        return result

class InvoiceParserPlugin:
    """This is a plugin to parse and extract information from invoices and extracts relevant pre-defined fields from it. Also produces a markdown representation of the invocies for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    def InvoiceParserPlugin(self, file_urls):
        analyzer_id = 'invoice-analyzer-agent-sample'
        analyzer_schema_file='../../../analyzer_templates/invoice.json'
        client = AzureContentUnderstandingClient()
        result = client.run_cu(file_urls, analyzer_id, analyzer_schema_file)
        return result

class MarketingVideoParserPlugin:
    """This is a plugin to parse and extract information from videos and extracts relevant pre-defined fields regarding marketing information from it. Also produces a markdown representation of the video segments for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    def MarketingVideoParserPlugin(self, file_urls):
        analyzer_id = 'marketing-video-analyzer-agent-sample'
        analyzer_schema_file='../../../analyzer_templates/marketing_video.json'
        client = AzureContentUnderstandingClient()
        result = client.run_cu(file_urls, analyzer_id, analyzer_schema_file)
        return result

# class DynamicFieldSchemaPlugin:
#     """This plugin dynamically generates a fieldSchema based on user requests and processes the data accordingly."""
#     @kernel_function
#     def DynamicFieldSchemaPlugin(self, user_request, file_urls):
#         # Generate the dynamic fieldSchema
#         dynamic_schema = generate_dynamic_field_schema(user_request)

#         # Use the dynamic schema to process the files
#         analyzer_id = 'dynamic-analyzer'
#         client = AzureContentUnderstandingClient()

#         # Create the analyzer dynamically
#         analyzer = client.begin_create_analyzer(
#             analyzer_id=analyzer_id,
#             analyzer_template={
#                 "description": "Dynamically generated analyzer",
#                 "scenario": "custom",
#                 "config": {
#                     "returnDetails": True,
#                     "locales": ["en-US"]
#                 },
#                 "fieldSchema": dynamic_schema
#             }
#         )

#         if analyzer.status_code != 201:
#             return {
#                 "error": "Failed to create dynamic analyzer."
#             }

#         # Process the files using the dynamic analyzer
#         result = client.run_cu(file_urls, analyzer_id, None)
#         return result