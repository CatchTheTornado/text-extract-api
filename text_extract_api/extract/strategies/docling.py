import tempfile

from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import (  # Assuming a compatible Docling library or module
    DoclingDocument,
)

from text_extract_api.extract.extract_result import ExtractResult
from text_extract_api.extract.strategies.strategy import Strategy
from text_extract_api.files.file_formats import FileFormat


class DoclingStrategy(Strategy):
    """
    Extraction strategy for processing PDF documents using Docling.
    """

    def name(self) -> str:
        return "docling"

    def extract_text(
        self, file_format: FileFormat, language: str = "en"
    ) -> ExtractResult:
        """
        Extracts text from a file using Docling and returns an ExtractResult.

        :param file_format: Instance of FileFormat (which supports most docling formats).
        :param language: Language of the text (default is 'en').
        :return: ExtractResult containing the extracted DoclingDocument and metadata.
        """

        # Save file content to a temporary file
        temp_file_path = self._save_to_temp_file(file_format)

        # Convert the document using Docling
        docling_document = self._convert_to_docling(temp_file_path)

        # Return the result wrapped in ExtractResult
        return ExtractResult(value=docling_document, text_gatherer=self.text_gatherer)

    def text_gatherer(self, docling_document: DoclingDocument) -> str:
        """
        Gathers text content from a DoclingDocument in markdown format.

        :param docling_document: Instance of DoclingDocument.
        :return: Text content in markdown format.
        """
        return docling_document.export_to_markdown()

    def _convert_to_docling(self, file_path: str) -> DoclingDocument:
        """
        Converts a file into a DoclingDocument instance.

        :param file_path: Path to the PDF file to be converted.
        :return: DoclingDocument instance.
        """
        # Placeholder for actual conversion logic using the Docling API
        try:
            converter = DocumentConverter()
            docling_document = converter.convert(file_path).document
            return docling_document
        except Exception as e:
            raise RuntimeError(f"Failed to convert document using Docling: {e}")

    def _save_to_temp_file(self, file_format: FileFormat) -> str:
        """
        Saves the content of a FileFormat instance to a temporary file.

        :param file_format: Instance of FileFormat.
        :return: Path to the temporary file containing the file content.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_format.binary)
            return temp_file.name
