import unittest
from unittest.mock import MagicMock, patch

from text_extract_api.files.converters.converter import Converter
from text_extract_api.files.file_formats.file_format import FileFormat


class TestConverter(unittest.TestCase):
    @patch(
        "text_extract_api.files.converters.converter.Converter.convert",
        return_value=iter(["page1", "page2", "page3"]),
    )
    def test_convert_to_list(self, mock_convert):
        file_format = MagicMock(spec=FileFormat)
        result = Converter.convert_to_list(file_format)
        self.assertEqual(result, ["page1", "page2", "page3"])
        mock_convert.assert_called_once_with(file_format)

    @patch(
        "text_extract_api.files.converters.converter.Converter.convert",
        return_value=iter(["page1", "page2", "page3"]),
    )
    def test_convert_force_single(self, mock_convert):
        file_format = MagicMock(spec=FileFormat)
        result = Converter.convert_force_single(file_format)
        self.assertEqual(result, "page1")
        mock_convert.assert_called_once_with(file_format)

    @patch(
        "text_extract_api.files.converters.converter.Converter.convert",
        side_effect=NotImplementedError,
    )
    def test_convert_not_implemented(self):
        file_format = MagicMock(spec=FileFormat)
        with self.assertRaises(NotImplementedError):
            list(Converter.convert(file_format))


if __name__ == "__main__":
    unittest.main()
