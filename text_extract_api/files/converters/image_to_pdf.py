from io import BytesIO
from typing import Iterator, Type
from PIL import Image
from files.converters.converter import Converter
from files.file_formats.image import ImageFileFormat
from files.file_formats.pdf import PdfFileFormat


class ImageToPdfConverter(Converter):
    @staticmethod
    def convert(file_format: ImageFileFormat) -> Iterator[Type["PdfFileFormat"]]:
        image = Image.open(BytesIO(file_format.binary))
        pdf_bytes = ImageToPdfConverter._image_to_pdf_bytes(image)
        yield PdfFileFormat.from_binary(
            binary=pdf_bytes,
            filename=f"{file_format.filename}.pdf",
            mime_type="application/pdf",
        )

    @staticmethod
    def _image_to_pdf_bytes(image: Image) -> bytes:
        buffer = BytesIO()
        image.save(buffer, format="PDF")
        return buffer.getvalue()
