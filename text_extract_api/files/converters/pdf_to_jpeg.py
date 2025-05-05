from __future__ import annotations
from typing import Iterator, Type
from pdf2image import convert_from_bytes

from text_extract_api.files.converters.converter import Converter
from text_extract_api.files.file_formats.image import ImageFileFormat
from text_extract_api.files.file_formats.pdf import PdfFileFormat


class PdfToJpegConverter(Converter):
    @staticmethod
    def convert(file_format: PdfFileFormat) -> Iterator[Type["ImageFileFormat"]]:
        pages = convert_from_bytes(file_format.binary)
        if not pages:
            raise ValueError("No pages found in the PDF.")
        for i, page in enumerate(pages, start=1):
            yield ImageFileFormat.from_binary(
                binary=PdfToJpegConverter._image_to_bytes(page),
                filename=f"{file_format.filename}_page_{i}.jpg",
                mime_type="image/jpeg",
            )

    @staticmethod
    def _image_to_bytes(image) -> bytes:
        from io import BytesIO

        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue()
