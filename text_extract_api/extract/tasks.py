import os
import time
from typing import Optional

import ollama
import redis

from text_extract_api.celery_app import app as celery_app
from text_extract_api.extract.strategies.strategy import Strategy
from text_extract_api.files.file_formats.file_format import FileFormat
from text_extract_api.files.storage_manager import StorageManager

# Connect to Redis
redis_url = os.getenv('REDIS_CACHE_URL', 'redis://redis:6379/1')
redis_client = redis.StrictRedis.from_url(redis_url)


@celery_app.task(bind=True)
def ocr_task(
        self,
        binary_content: bytes,
        strategy_name: str,
        filename: str,
        file_hash: str,
        ocr_cache: bool,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        language: Optional[str] = None,
        storage_profile: Optional[str] = None,
        storage_filename: Optional[str] = None,
        verify_document: bool = False,
        document_path: Optional[str] = None,
):
    """
    Celery task to perform OCR processing on a PDF/Office/image file.
    When verify_document is True, the original file (document_path) is also
    inspected for authenticity via the Stipple API (free tier) and the
    warrant is attached to the result under document_verification.
    """
    start_time = time.time()

    strategy = Strategy.get_strategy(strategy_name)
    strategy.set_update_state_callback(self.update_state)

    self.update_state(state='PROGRESS', status="File uploaded successfully",
                      meta={'progress': 10})  # Example progress update

    extracted_text = None
    if ocr_cache:
        cached_result = redis_client.get(file_hash)
        if cached_result:
            # Return cached result if available
            extracted_text = cached_result.decode('utf-8')

    if extracted_text is None:
        print(f"Extracting text from file using strategy: {strategy.name()}")
        self.update_state(state='PROGRESS',
                          meta={'progress': 30, 'status': 'Extracting text from file', 'start_time': start_time,
                                'elapsed_time': time.time() - start_time})  # Example progress update
        extract_result = strategy.extract_text(FileFormat.from_binary(binary_content), language)
        extracted_text = extract_result.text

    else:
        print("Using cached result...")

    print("After extracted text")
    self.update_state(state='PROGRESS',
                      meta={'progress': 50, 'status': 'Text extracted', 'extracted_text': extracted_text,
                            'start_time': start_time,
                            'elapsed_time': time.time() - start_time})  # Example progress update

    # @todo Universal Text Object - is cache available
    if ocr_cache:
        redis_client.set(file_hash, extracted_text)

    if prompt:
        print(f"Transforming text using LLM (prompt={prompt}, model={model}) ...")
        self.update_state(state='PROGRESS', meta={'progress': 75, 'status': 'Processing LLM', 'start_time': start_time,
                                                  'elapsed_time': time.time() - start_time})  # Example progress update
        llm_resp = ollama.generate(model, prompt + extracted_text, stream=True)
        num_chunk = 1
        extracted_text = ''  # will be filled with chunks from llm
        for chunk in llm_resp:
            self.update_state(state='PROGRESS',
                              meta={'progress': num_chunk, 'status': 'LLM Processing chunk no: ' + str(num_chunk),
                                    'start_time': start_time,
                                    'elapsed_time': time.time() - start_time})  # Example progress update
            num_chunk += 1
            extracted_text += chunk['response']

    if storage_profile:
        if not storage_filename:
            storage_filename = filename.replace('.', '_') + '.pdf'

        storage_manager = StorageManager(storage_profile)
        storage_manager.save(filename, storage_filename, extracted_text)

    document_verification = None
    if verify_document and document_path:
        try:
            from text_extract_api.extract.stipple_verification import verification_block
            document_verification = verification_block(document_path, enabled=True)
        except Exception as e:  # noqa: BLE001 - verification must never break extraction
            print(f"Stipple verification failed (non-fatal): {e}")

    self.update_state(state='DONE', meta={'progress': 100, 'status': 'Processing done!', 'start_time': start_time,
                                          'elapsed_time': time.time() - start_time})

    if document_verification is not None:
        return {"extracted_text": extracted_text, "document_verification": document_verification}
    return extracted_text
