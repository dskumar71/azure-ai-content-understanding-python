from semantic_kernel.functions import kernel_function
from plugins.cu_extract_fields import cu_extract_fields

class TenKParserPlugin:
    """Parses the 10K PDF and extracts the relevant fields from the document. Also produces a markdown representation of the document for adding to a vector store for RAG"""
    analyzer_id = 'financial-analyzer11'
    analyzer_schema_file='../../../analyzer_templates/financial_report.json'

    @kernel_function
    def parse_data(self, file_url):
        result = cu_extract_fields().extract_fields(file_url, self.analyzer_id, self.analyzer_schema_file)
        return result
