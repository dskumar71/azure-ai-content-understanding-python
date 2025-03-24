import json
from semantic_kernel.functions import kernel_function
from plugins.cu_extract_fields import cu_extract_fields

class TenKParserPlugin:
    """Parses the 10K PDF and extracts the relevant fields from the document. Also produces a markdown representation of the document for adding to a vector store for RAG."""
    @kernel_function
    def TenKParserPlugin(self, file_url):
        analyzer_id = 'financial-analyzer11'
        analyzer_schema_file='../../../analyzer_templates/financial_report.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.loads(f.read())
        print(analyzer_id)
        print(analyzer_schema)
        print(file_url)
        result = cu_extract_fields().run_cu(file_url, analyzer_id, analyzer_schema)
        return result

class CallCenterRecordingParserPlugin:
    """Parses the call recording audio files and extracts the relevant fields from it. Also produces a markdown representation of the audio transcript as WEBVTT for adding to a vector store for RAG."""
    @kernel_function
    def CallCenterRecordingParserPlugin(self, file_url):
        analyzer_id = 'callcenter-analyzer11'
        analyzer_schema_file='../../../analyzer_templates/call_recording_analytics.json'
        with open(analyzer_schema_file, "r") as f:
            analyzer_schema = json.loads(f.read())
        print(analyzer_id)
        print(analyzer_schema)
        print(file_url)
        result = cu_extract_fields().run_cu(file_url, analyzer_id, analyzer_schema)
        return result