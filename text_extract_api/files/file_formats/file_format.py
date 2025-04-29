import base64
from hashlib import md5
from typing import Type, Iterator, Optional, Dict, Callable, List, TypedDict

import magic


class FileFormatDict(TypedDict):
    filename: str
    mime_type: str
    binary_file_content_size: int
    content_base64: Optional[str]
    content_binary: Optional[bytes]


class FileFormat:
    DEFAULT_FILENAME: str = "file"
    DEFAULT_MIME_TYPE: Optional[str] = None
    _base64_cache: Optional[str] = None

    # Construction

    def __init__(
        self,
        binary_file_content: bytes,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> None:
        """
        Attributes:
            binary_file_content (bytes): The binary content of the file.
            filename (str): The name of the file. Defaults to a predefined
                value if not provided.
            mime_type (str): The MIME type of the file. Defaults to a
                predefined value if not provided.

        Parameters:
            binary_file_content: The binary content of the file.
            filename: The name of the file. Defaults to None.
            mime_type: The MIME type. Defaults to None.

        Raises:
            ValueError: If binary_file_content is empty or if no MIME type
                is provided or defaulted to.
        """
        if not binary_file_content:
            raise ValueError(
                f"{self.__class__.__name__} missing content file - corrupted base64 or binary data."
            )

        resolved_mime_type = mime_type or self.DEFAULT_MIME_TYPE
        if not resolved_mime_type:
            raise ValueError(
                f"{self.__class__.__name__} requires a mime type to be provided or defaulted."
            )

        self.binary_file_content: bytes = binary_file_content
        self.filename: str = filename or self.DEFAULT_FILENAME
        self.mime_type: str = resolved_mime_type

    @classmethod
    def from_base64(
        cls,
        base64_string: str,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Type["FileFormat"]:
        binary = base64.b64decode(base64_string)
        instance = cls.from_binary(binary, filename=filename, mime_type=mime_type)
        instance._base64_cache = base64_string
        return instance

    @classmethod
    def from_binary(
        cls,
        binary: bytes,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Type["FileFormat"]:
        if mime_type == "application/octet-stream":
            mime_type = None
        mime_type = mime_type or FileFormat._guess_mime_type(
            binary_data=binary, filename=filename
        )
        file_format_class = cls._get_file_format_class(mime_type)
        return file_format_class(
            binary_file_content=binary, filename=filename, mime_type=mime_type
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the FileFormat instance.
        """
        size = len(self.binary_file_content)
        return f"<FileFormat(filename='{self.filename}', mime_type='{self.mime_type}', size={size} bytes)>"

    def to_dict(self, encode_base64: bool = False) -> FileFormatDict:
        """
        Converts the FileFormat instance to a dictionary.

        Args:
            encode_base64 (bool): If True, includes Base64-encoded content;
                otherwise includes binary content.

        Returns:
            FileFormatDict: A dictionary containing the file's details,
                including either Base64 or binary content.
        """
        return {
            "filename": self.filename,
            "mime_type": self.mime_type,
            "binary_file_content_size": len(self.binary_file_content),
            "content_base64": self.base64_content if encode_base64 else None,
            "content_binary": self.binary_file_content if not encode_base64 else None,
        }

    @property
    def base64_(self) -> str:
        if self._base64_cache is None:
            self._base64_cache = base64.b64encode(self.binary_file_content).decode(
                "utf-8"
            )
        return self._base64_cache

    @property
    def hash(self) -> str:
        return md5(self.binary).hexdigest()

    @property
    def binary(self) -> bytes:
        return self.binary_file_content

    def iterator(self, target_format: Optional["FileFormat"]) -> Iterator["FileFormat"]:
        """
        Return an iterator of a file(s)

        By default, the iterator uses the format defined by `default_iterator_file_format()`.
        If a `target_format` is provided, it must be compatible and convertible using
        `convertible_to()`.

        Args:
            target_format (Optional[Type[FileFormat]]): The desired file format for conversion.

        Returns:
            Iterator[FileFormat]: An iterator for the specified or default file format.

        Raises:
            ValueError: If the target format is not compatible or convertible.
        """
        final_format = target_format or self.default_iterator_file_format

        if self.is_pageable():
            if final_format.is_pageable():
                raise ValueError(
                    "Target format and current format are both pageable. Cannot iterate."
                )
            else:
                yield self.convert_to(final_format)
        else:
            yield self.convert_to(final_format)

    # Utils
    @staticmethod
    def accepted_mime_types() -> list[str]:
        raise NotImplementedError("Subclasses must implement accepted_mime_types.")

    @staticmethod
    def is_pageable() -> bool:
        """
        Checks if the format supports pagination. Pdf does, image does not. :)
        """
        raise NotImplementedError("Subclasses must implement is_pageable.")

    def can_convert_to(self, target_format: "FileFormat") -> bool:
        convertible_keys = self.convertible_to().keys()
        return any(target_format is key for key in convertible_keys)

    def convert_to(self, target_format: Type["FileFormat"]) -> List["FileFormat"]:
        if isinstance(self, target_format):
            return [self]

        converters = self.convertible_to()
        if target_format not in converters:
            raise ValueError(
                f"Cannot convert to {target_format}. Conversion not supported."
            )

        return list(converters[target_format](self))

    @staticmethod
    def convertible_to() -> Dict[
        Type["FileFormat"], Callable[[Type["FileFormat"]], Iterator[Type["Converter"]]]  # NOQA: F821
    ]:
        """
        Defines what formats this file type can be converted to.
        Returns a dictionary where keys are target formats and values are functions
        that produce FileFormat instances.

        :return: A dictionary of convertible formats and their converters.
        """
        return {}  # To check, Converter is not defined in this file

    @classmethod
    def default_iterator_file_format(cls) -> Type["FileFormat"]:
        if not cls.is_pageable():
            return cls
        raise NotImplementedError(
            "Pageable formats must implement default_iterator_file_format."
        )

    def unify(self) -> "FileFormat":
        """
        Converts the file to a universal type for that format (e.g., JPEG from png, bmp, tiff, etc.).
        Default implementation returns a new instance of the current format.

        :return: Unified format as a new self instance.
        """
        return self

    @staticmethod
    def _get_file_format_class(mime_type: str) -> Type["FileFormat"]:
        import text_extract_api.files.file_formats.pdf  # noqa - its not unused import @todo autodiscover
        import text_extract_api.files.file_formats.image  # noqa - its not unused import @todo autodiscover
        import text_extract_api.files.file_formats.docling  # noqa - its not unused import @todo autodiscover

        for subclass in FileFormat.__subclasses__():
            if mime_type in subclass.accepted_mime_types():
                return subclass
        raise ValueError(f"No matching FileFormat class for mime type: {mime_type}")

    @staticmethod
    def _guess_mime_type(
        binary_data: Optional[bytes] = None, filename: Optional[str] = None
    ) -> str:
        mime = magic.Magic(mime=True)
        if binary_data:
            return mime.from_buffer(binary_data)
        if filename:
            return mime.from_file(filename)
        raise ValueError(
            "Either binary_data or filename must be provided to guess the MIME type."
        )


class FileField:
    def __init__(self, value: str):
        self._file_format = FileFormat.from_base64(value)
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __get_pydantic_core_schema__(self, handler) -> str:
        return handler.generate_schema(str)
