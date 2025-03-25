import json
from semantic_kernel.functions import kernel_function
from plugins.cu_extract_fields import cu_extract_fields

class TenKParserPlugin:
    """This is a plugin to parse annual financial reports also known as 10K files and extracts the relevant fields from the document. It should only be used for this type of file. Also produces a markdown representation of the document for adding to a vector store for RAG."""
    @kernel_function
    def TenKParserPlugin(self, file_urls):
        analyzer_id = 'financial-analyzer11'
        analyzer_schema_file='../../../analyzer_templates/financial_report.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.loads(f.read())
        print("\n")
        print(analyzer_id)
        print(analyzer_schema)
        print(file_urls)
        result = cu_extract_fields().run_cu(file_urls, analyzer_id, analyzer_schema)
        return result

class CallCenterRecordingParserPlugin:
    """This is a plugin to parse and extract information from call recording audio files and extracts relevant pre-defined fields from it. Also produces a markdown representation of the audio transcript as WEBVTT for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    def CallCenterRecordingParserPlugin(self, file_urls):
        analyzer_id = 'callcenter-analyzer11'
        analyzer_schema_file='../../../analyzer_templates/call_recording_analytics.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.loads(f.read())
        print("\n")
        print(analyzer_id)
        print(analyzer_schema)
        print(file_urls)
        result = cu_extract_fields().run_cu(file_urls, analyzer_id, analyzer_schema)
        return result
    
class InvoiceParserPlugin:
    """This is a plugin to parse and extract information from invoices and extracts relevant pre-defined fields from it. Also produces a markdown representation of the invocies for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    def InvoiceParserPlugin(self, file_urls):
        analyzer_id = 'invoice-analyzer11'
        analyzer_schema_file='../../../analyzer_templates/invoice.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.loads(f.read())
        print("\n")
        print(analyzer_id)
        print(analyzer_schema)
        print(file_urls)
        result = cu_extract_fields().run_cu(file_urls, analyzer_id, analyzer_schema)
        return result
    
class MarketingVideoParserPlugin:
    """This is a plugin to parse and extract information from videos and extracts relevant pre-defined fields regarding marketing information from it. Also produces a markdown representation of the video segments for adding to a vector store for RAG or answer additional questions not part of the plugin results with."""
    @kernel_function
    def InvoiceParserPlugin(self, file_urls):
        analyzer_id = 'marketing-video-analyzer11'
        analyzer_schema_file='../../../analyzer_templates/marketing_video.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.loads(f.read())
        print("\n")
        print(analyzer_id)
        print(analyzer_schema)
        print(file_urls)
        result = cu_extract_fields().run_cu(file_urls, analyzer_id, analyzer_schema)
        return result   