import io
import numpy as np
from PIL import Image
import easyocr

from extract.extract_result import ExtractResult
from text_extract_api.extract.strategies.strategy import Strategy
from text_extract_api.files.file_formats.file_format import FileFormat
from text_extract_api.files.file_formats.image import ImageFileFormat


class EasyOCRStrategy(Strategy):
    @classmethod
    def name(cls) -> str:
        return "easyOCR"

    def extract_text(
        self, file_format: FileFormat, language: str = "en"
    ) -> ExtractResult:
        """
        Extract text using EasyOCR after converting the input file to images
        (if not already an ImageFileFormat).
        """

        # Ensure we can actually convert the input file to ImageFileFormat
        if not isinstance(
            file_format, ImageFileFormat
        ) and not file_format.can_convert_to(ImageFileFormat):
            raise TypeError(
                f"EasyOCR - format {file_format.mime_type} is not supported (yet?)"
            )

        # Convert the input file to a list of ImageFileFormat objects
        images = FileFormat.convert_to(file_format, ImageFileFormat)

        # Initialize the EasyOCR Reader
        # Add or change languages to your needs, e.g., ['en', 'fr']
        reader = easyocr.Reader(language.split(","))

        # Process each image, extracting text
        all_extracted_text = []
        for image_format in images:
            # Convert the in-memory bytes to a PIL Image
            pil_image = Image.open(io.BytesIO(image_format.binary))

            # Convert PIL image to numpy array for EasyOCR
            np_image = np.array(pil_image)

            # Perform OCR; with `detail=0`, we get just text, no bounding boxes
            ocr_result = reader.readtext(
                np_image, detail=0
            )  # TODO: addd bounding boxes support as described in #37

            # Combine all lines into a single string for that image/page
            extracted_text = "\n".join(ocr_result)
            all_extracted_text.append(extracted_text)

        # Join text from all images/pages
        full_text = "\n\n".join(all_extracted_text)

        return ExtractResult.from_text(full_text)
