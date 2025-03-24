from semantic_kernel.functions import kernel_function
from plugins.cu_extract_fields import cu_extract_fields

class CallCenterRecordingParserPlugin:
    """Parses the call recording audio files and extracts the relevant fields from it. Also produces a markdown representation of the audio transcript as WEBVTT for adding to a vector store for RAG."""
    analyzer_id = 'callcenter-analyzer11'
    analyzer_schema_file='../../../analyzer_templates/call_recording_analytics.json'

    @kernel_function
    def parse_data(self, file_url):
        result = cu_extract_fields().extract_fields(file_url, self.analyzer_id, self.analyzer_schema_file)
        return result
