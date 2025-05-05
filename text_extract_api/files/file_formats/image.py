from enum import Enum
from typing import Callable, Dict, Iterator, Type
from io import BytesIO
from PIL import Image

from text_extract_api.files.file_formats.file_format import FileFormat


class ImageSupportedExportFormats(Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    BMP = "BMP"
    TIFF = "TIFF"


class ImageFileFormat(FileFormat):
    DEFAULT_FILENAME: str = "image.jpeg"

    @staticmethod
    def accepted_mime_types() -> list[str]:
        return ["image/jpeg", "image/png", "image/bmp", "image/gif", "image/tiff"]

    @staticmethod
    def convertible_to() -> Dict[
        Type["FileFormat"], Callable[[], Iterator["FileFormat"]]
    ]:
        from text_extract_api.files.file_formats.pdf import PdfFileFormat
        from text_extract_api.files.converters.image_to_pdf import ImageToPdfConverter

        return {PdfFileFormat: ImageToPdfConverter.convert}

    @staticmethod
    def is_pageable() -> bool:
        return False

    @classmethod
    def default_iterator_file_format(cls) -> Type["ImageFileFormat"]:
        return cls

    def unify(self) -> "FileFormat":
        unified_image = ImageProcessor.unify_image(
            self.binary, ImageSupportedExportFormats.JPEG
        )
        return ImageFileFormat.from_binary(unified_image, self.filename, self.mime_type)

    @staticmethod
    def validate(binary_file_content: bytes):
        try:
            with Image.open(BytesIO(binary_file_content)) as img:
                img.verify()
        except OSError as e:
            raise ValueError("Corrupted image file content") from e


class ImageProcessor:
    @staticmethod
    def unify_image(
        image_bytes: bytes,
        target_format: ImageSupportedExportFormats = "JPEG",
        convert_to_rgb: bool = True,
    ) -> bytes:
        """
        Prepares an image for OCR by unifying its format and color mode.
        - Converts image to the desired format (e.g., JPEG).
        - Converts grayscale, CMYK, etc., to RGB (if required).
        :param image_bytes: Input image in bytes.
        :param target_format: Desired format for the output image (default: JPEG)
        :param convert_to_rgb: Convert to RGB format if not already (default: True).
        :return:Image bytes in the new format.
        """
        image = Image.open(BytesIO(image_bytes))

        # We need RGB - problem occurred when P (png) was sent
        if convert_to_rgb and image.mode != "RGB":
            image = image.convert("RGB")

        buffered = BytesIO()
        image.save(buffered, format=target_format.value)
        return buffered.getvalue()
