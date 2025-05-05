from typing import Type, Dict, Callable, Iterator
from text_extract_api.files.file_formats.file_format import FileFormat


class DoclingFileFormat(FileFormat):
    DEFAULT_FILENAME: str = "document.docling"
    DEFAULT_MIME_TYPE: str = "application/vnd.docling"

    @staticmethod
    def accepted_mime_types() -> list[str]:
        return [
            "application/vnd.docling",  # Docling documents
            # Do not put all formats handled by docling here - only those that are not supported by dedicated file formats"
            "text/plain",
            "text/markdown",
            "text/html",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.oasis.opendocument.text",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/csv",
            "application/json",
            "application/xml",
        ]

    @staticmethod
    def is_pageable() -> bool:
        return True

    @classmethod
    def default_iterator_file_format(cls) -> Type[FileFormat]:
        return cls

    @staticmethod
    def convertible_to() -> Dict[
        Type["FileFormat"], Callable[[], Iterator["FileFormat"]]
    ]:
        # No specific converters needed as the strategy will handle conversion
        return {}

    @staticmethod
    def validate(binary_file_content: bytes):
        if not binary_file_content or len(binary_file_content) == 0:
            raise ValueError("Empty file content")
