import pytesseract
import cv2
import numpy as np
from ocr_strategies.ocr_strategy import OCRStrategy
from pdf2image import convert_from_bytes

class TesseractOCRStrategy(OCRStrategy):
    """Tesseract OCR Strategy"""
    def extract_text_from_pdf(self, pdf_bytes):
        images = convert_from_bytes(pdf_bytes)
        extracted_text = ""

        for i, image in enumerate(images):
            rgb_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
            page_text = pytesseract.image_to_string(rgb_image)
            extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text
