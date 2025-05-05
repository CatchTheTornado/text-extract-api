import os
import tempfile
import time

import httpx
from ollama import Client

from extract.extract_result import ExtractResult
from text_extract_api.extract.strategies.strategy import Strategy
from text_extract_api.files.file_formats.file_format import FileFormat
from text_extract_api.files.file_formats.image import ImageFileFormat


class OllamaStrategy(Strategy):
    """Ollama models OCR strategy"""

    @classmethod
    def name(cls) -> str:
        return "llama_vision"

    def extract_text(
        self, file_format: FileFormat, language: str = "en"
    ) -> ExtractResult:
        if not isinstance(
            file_format, ImageFileFormat
        ) and not file_format.can_convert_to(ImageFileFormat):
            raise TypeError(
                f"Ollama OCR - format {file_format.mime_type} is not supported (yet?)"
            )
        images = FileFormat.convert_to(file_format, ImageFileFormat)
        extracted_text = ""
        start_time = time.time()
        ocr_percent_done = 0
        num_pages = len(images)
        for i, image in enumerate(images):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_file.write(image.binary)
                temp_filename = temp_file.name

            # Generate text using the specified model
            try:
                timeout = httpx.Timeout(
                    connect=180.0, read=180.0, write=180.0, pool=180.0
                )  # @todo move those values to .env
                ollama = Client(timeout=timeout)
                response = ollama.chat(
                    self._strategy_config.get("model"),
                    [
                        {
                            "role": "user",
                            "content": self._strategy_config.get("prompt"),
                            "images": [temp_filename],
                        }
                    ],
                    stream=True,
                )
                os.remove(temp_filename)
                num_chunk = 1
                for chunk in response:
                    meta = {
                        "progress": str(30 + ocr_percent_done),
                        "status": "OCR Processing"
                        + "(page "
                        + str(i + 1)
                        + " of "
                        + str(num_pages)
                        + ")"
                        + " chunk no: "
                        + str(num_chunk),
                        "start_time": start_time,
                        "elapsed_time": time.time() - start_time,
                    }
                    self.update_state_callback(state="PROGRESS", meta=meta)
                    num_chunk += 1
                    extracted_text += chunk["message"]["content"]

                ocr_percent_done += int(
                    20 / num_pages
                )  # 20% of work is for OCR - just a stupid assumption from tasks.py
            except ollama.ResponseError as e:
                print("Error:", e.error)
                raise Exception(
                    "Failed to generate text with Ollama model "
                    + self._strategy_config.get("model")
                )

            print(response)

        return ExtractResult.from_text(extracted_text)
