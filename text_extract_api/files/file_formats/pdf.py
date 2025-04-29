from typing import Type, Callable, Dict, Iterator

from text_extract_api.files.file_formats.file_format import FileFormat


class PdfFileFormat(FileFormat):
    DEFAULT_FILENAME: str = "image.pdf"

    @staticmethod
    def accepted_mime_types() -> list[str]:
        return ["application/pdf"]

    @staticmethod
    def is_pageable() -> bool:
        return True

    @classmethod
    def default_iterator_file_format(cls) -> Type[FileFormat]:
        from text_extract_api.files.file_formats.image import ImageFileFormat

        return ImageFileFormat

    @staticmethod
    def convertible_to() -> Dict[
        Type["FileFormat"], Callable[[], Iterator["FileFormat"]]
    ]:
        from text_extract_api.files.file_formats.image import ImageFileFormat
        from text_extract_api.files.converters.pdf_to_jpeg import PdfToJpegConverter

        return {ImageFileFormat: PdfToJpegConverter.convert}

    @staticmethod
    def validate(binary_file_content: bytes):
        if not binary_file_content.startswith(b"%PDF"):
            raise ValueError("Corrupted PDF file")
