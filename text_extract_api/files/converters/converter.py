from typing import Iterator, List, Type

from text_extract_api.files.file_formats.file_format import FileFormat


class Converter:
    @staticmethod
    def convert(file_format: Type["FileFormat"]) -> Iterator["FileFormat"]:
        raise NotImplementedError("Subclasses must implement the `convert` method.")

    @classmethod
    def convert_to_list(cls, file_format: Type["FileFormat"]) -> List["FileFormat"]:
        return list(cls.convert(file_format))

    @classmethod
    def convert_force_single(
        cls, file_format: Type["FileFormat"]
    ) -> Type["FileFormat"]:
        """Warning - this will return only first page"""
        return next(cls.convert(file_format), None)
