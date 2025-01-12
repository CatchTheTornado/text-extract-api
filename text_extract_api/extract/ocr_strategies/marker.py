from marker.convert import convert_single_pdf
from marker.models import load_all_models

from text_extract_api.extract.ocr_strategies.ocr_strategy import OCRStrategy
from text_extract_api.files.file_formats.file_format import FileFormat
from text_extract_api.files.file_formats.pdf_file_format import PdfFileFormat


class MarkerOCRStrategy(OCRStrategy):

    @classmethod
    def name(cls) -> str:
        return "marker"

    def extract_text(self, file_format: FileFormat):
        if not isinstance(file_format, PdfFileFormat):
            raise TypeError(
                f"Marker - format {file_format.mime_type} is not supported (yet?)"
            )


        model_lst = load_all_models()
        full_text, images, out_meta = convert_single_pdf(file_format.binary, model_lst)
        return full_text
