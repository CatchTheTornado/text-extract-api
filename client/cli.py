import argparse
import base64
import requests
import time
import os
import math
from ollama import pull


def ocr_upload(
    file_path,
    ocr_cache,
    prompt,
    prompt_file=None,
    model="llama3.1",
    strategy="llama_vision",
    storage_profile="default",
    storage_filename=None,
    language="en",
):
    ocr_url = os.getenv("OCR_UPLOAD_URL", "http://localhost:8000/ocr/upload")
    files = {"file": open(file_path, "rb")}
    if not ocr_cache:
        print("OCR cache disabled.")

    data = {
        "ocr_cache": ocr_cache,
        "model": model,
        "strategy": strategy,
        "storage_profile": storage_profile,
        "language": language,
    }

    if storage_filename:
        data["storage_filename"] = storage_filename

    print(data)  # @todo change to log debug in the future

    try:
        if prompt_file:
            prompt = open(prompt_file, "r").read()
    except FileNotFoundError:
        print(f"Prompt file not found: {prompt_file}")
        return None

    if prompt:
        data["prompt"] = prompt

    response = requests.post(ocr_url, files=files, data=data)
    if response.status_code == 200:
        respObject = response.json()
        if respObject.get("task_id"):
            return {"task_id": respObject.get("task_id")}
        else:
            return {
                "text": respObject.get("text")  # sync mode support
            }
    else:
        print(f"Failed to upload file: {response.text}")
        return None


def ocr_request(
    file_path,
    ocr_cache,
    prompt,
    prompt_file=None,
    model="llama3.1",
    strategy="llama_vision",
    storage_profile="default",
    storage_filename=None,
    language="en",
):
    ocr_url = os.getenv("OCR_REQUEST_URL", "http://localhost:8000/ocr/request")
    with open(file_path, "rb") as f:
        file_content = base64.b64encode(f.read()).decode("utf-8")

    data = {
        "ocr_cache": ocr_cache,
        "model": model,
        "strategy": strategy,
        "storage_profile": storage_profile,
        "file": file_content,
        "language": language,
    }

    if storage_filename:
        data["storage_filename"] = storage_filename

    if prompt_file:
        try:
            prompt = open(prompt_file, "r").read()
        except FileNotFoundError:
            print(f"Prompt file not found: {prompt_file}")
            return None

    if prompt:
        data["prompt"] = prompt

    response = requests.post(ocr_url, json=data)
    if response.status_code == 200:
        respObject = response.json()
        if respObject.get("task_id"):
            return {"task_id": respObject.get("task_id")}
        else:
            return {
                "text": respObject.get("text")  # sync mode support
            }
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_result(task_id, print_progress=False):
    extracted_text_printed_once = False
    result_url = os.getenv("RESULT_URL", "http://localhost:8000/ocr/result/")
    while True:
        response = requests.get(result_url + task_id)
        result = response.json()
        if result["state"] != "SUCCESS" and print_progress:
            task_info = result.get("info")
            if task_info is not None:
                if task_info.get("extracted_text"):
                    if not extracted_text_printed_once:
                        extracted_text_printed_once = True
                        print("Extracted text: " + task_info.get("extracted_text"))
                    else:
                        del task_info["extracted_text"]
                del task_info["start_time"]
            print(result)
        if response.status_code == 200:
            if result["state"] == "SUCCESS":
                return result["result"]
            elif result["state"] == "FAILURE":
                print("OCR task failed.")
                return None
        time.sleep(2)  # Wait for 2 seconds before checking again


def clear_cache():
    clear_cache_url = os.getenv(
        "CLEAR_CACHE_URL", "http://localhost:8000/ocr/clear_cache"
    )
    response = requests.post(clear_cache_url)
    if response.status_code == 200:
        print("OCR cache cleared successfully.")
    else:
        print(f"Failed to clear OCR cache: {response.text}")


def llm_pull(model="llama3.1"):
    response = pull(model, stream=True)
    for chunk in response:
        if chunk.completed and chunk.total:
            print(
                f"Please wait .... {model} - {chunk.status} - {math.floor((chunk.completed / chunk.total) * 100)}% completed"
            )
        else:
            print(f"Pulling {model} - {chunk.status}")


def llm_generate(prompt, model="llama3.1"):
    ollama_url = os.getenv("LLM_GENERATE_API_URL", "http://localhost:8000/llm/generate")
    response = requests.post(ollama_url, json={"model": model, "prompt": prompt})
    if response.status_code == 200:
        print(response.json().get("generated_text"))
    else:
        print(f"Failed to generate text: {response.text}")


def list_files(storage_profile):
    list_files_url = os.getenv("LIST_FILES_URL", "http://localhost:8000/storage/list")
    response = requests.get(list_files_url, params={"storage_profile": storage_profile})
    if response.status_code == 200:
        files = response.json().get("files", [])
        for file in files:
            print(file)
    else:
        print(f"Failed to list files: {response.text}")


def load_file(file_name, storage_profile):
    load_file_url = os.getenv("LOAD_FILE_URL", "http://localhost:8000/storage/load")
    response = requests.get(
        load_file_url,
        params={"file_name": file_name, "storage_profile": storage_profile},
    )
    if response.status_code == 200:
        content = response.json().get("content", "")
        print(content)
    else:
        print(f"Failed to load file: {response.text}")


def delete_file(file_name, storage_profile):
    delete_file_url = os.getenv(
        "DELETE_FILE_URL", "http://localhost:8000/storage/delete"
    )
    response = requests.delete(
        delete_file_url,
        params={"file_name": file_name, "storage_profile": storage_profile},
    )
    if response.status_code == 200:
        print(f"File {file_name} deleted successfully.")
    else:
        print(f"Failed to delete file: {response.text}")


def main():
    parser = argparse.ArgumentParser(description="CLI for OCR and Ollama operations.")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Sub-command for uploading a file via file upload
    ocr_parser = subparsers.add_parser(
        "ocr_upload", help="Upload a file to the OCR endpoint and get the result."
    )
    ocr_parser.add_argument(
        "--file",
        type=str,
        default="examples/rmi-example.pdf",
        help="Path to the file to upload",
    )
    ocr_parser.add_argument(
        "--ocr_cache",
        default=True,
        action="store_true",
        help="Enable OCR result caching",
    )
    ocr_parser.add_argument(
        "--disable_ocr_cache",
        default=False,
        action="store_true",
        help="Disable OCR result caching",
    )
    ocr_parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt used for the Ollama model to fix or transform the file",
    )
    ocr_parser.add_argument(
        "--prompt_file",
        default=None,
        type=str,
        help="Prompt file name used for the Ollama model to fix or transform the file",
    )
    ocr_parser.add_argument(
        "--model",
        type=str,
        default="llama3.1",
        help="Model to use for the Ollama endpoint",
    )
    ocr_parser.add_argument(
        "--strategy",
        type=str,
        default="llama_vision",
        help="OCR strategy to use for the file",
    )
    ocr_parser.add_argument(
        "--print_progress",
        default=True,
        action="store_true",
        help="Print the progress of the OCR task",
    )
    ocr_parser.add_argument(
        "--storage_profile",
        type=str,
        default="default",
        help="Storage profile to use for the file",
    )
    ocr_parser.add_argument(
        "--storage_filename",
        type=str,
        default=None,
        help="Storage filename to use for the file. You may use some formatting - see the docs",
    )
    ocr_parser.add_argument(
        "--language", type=str, default="en", help="Language to use for the OCR task"
    )
    # ocr_parser.add_argument('--async_mode', action='store_true', help='Enable async mode for the OCR task')

    # Sub-command for uploading a file via file upload - @deprecated - it's a backward compatibility gimmick
    ocr_parser = subparsers.add_parser(
        "ocr", help="Upload a file to the OCR endpoint and get the result."
    )
    ocr_parser.add_argument(
        "--file",
        type=str,
        default="examples/rmi-example.pdf",
        help="Path to the file to upload",
    )
    ocr_parser.add_argument(
        "--ocr_cache",
        default=True,
        action="store_true",
        help="Enable OCR result caching",
    )
    ocr_parser.add_argument(
        "--disable_ocr_cache",
        default=False,
        action="store_true",
        help="Disable OCR result caching",
    )
    ocr_parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt used for the Ollama model to fix or transform the file",
    )
    ocr_parser.add_argument(
        "--prompt_file",
        default=None,
        type=str,
        help="Prompt file name used for the Ollama model to fix or transform the file",
    )
    ocr_parser.add_argument(
        "--model",
        type=str,
        default="llama3.1",
        help="Model to use for the Ollama endpoint",
    )
    ocr_parser.add_argument(
        "--strategy",
        type=str,
        default="llama_vision",
        help="OCR strategy to use for the file",
    )
    ocr_parser.add_argument(
        "--print_progress",
        default=True,
        action="store_true",
        help="Print the progress of the OCR task",
    )
    ocr_parser.add_argument(
        "--storage_profile",
        type=str,
        default="default",
        help="Storage profile to use for the file",
    )
    ocr_parser.add_argument(
        "--storage_filename",
        type=str,
        default=None,
        help="Storage filename to use for the file. You may use some formatting - see the docs",
    )
    ocr_parser.add_argument(
        "--language", type=str, default="en", help="Language to use for the OCR task"
    )
    # ocr_parser.add_argument('--async_mode', action='store_true', help='Enable async mode for the OCR task')

    # Sub-command for uploading a file via request JSON
    ocr_request_parser = subparsers.add_parser(
        "ocr_request",
        help="Upload a file to the OCR endpoint via JSON and get the result.",
    )
    ocr_request_parser.add_argument(
        "--file",
        type=str,
        default="examples/rmi-example.pdf",
        help="Path to the file to upload",
    )
    ocr_request_parser.add_argument(
        "--ocr_cache",
        default=True,
        action="store_true",
        help="Enable OCR result caching",
    )
    ocr_request_parser.add_argument(
        "--disable_ocr_cache",
        default=False,
        action="store_true",
        help="Disable OCR result caching",
    )
    ocr_request_parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt used for the Ollama model to fix or transform the file",
    )
    ocr_request_parser.add_argument(
        "--prompt_file",
        default=None,
        type=str,
        help="Prompt file name used for the Ollama model to fix or transform the file",
    )
    ocr_request_parser.add_argument(
        "--model",
        type=str,
        default="llama3.1",
        help="Model to use for the Ollama endpoint",
    )
    ocr_request_parser.add_argument(
        "--strategy", type=str, default="llama_vision", help="OCR strategy to use"
    )
    ocr_request_parser.add_argument(
        "--print_progress",
        default=True,
        action="store_true",
        help="Print the progress of the OCR task",
    )
    ocr_request_parser.add_argument(
        "--storage_profile",
        type=str,
        default="default",
        help="Storage profile to use. You may use some formatting - see the docs",
    )
    ocr_request_parser.add_argument(
        "--storage_filename", type=str, default=None, help="Storage filename to use"
    )
    ocr_request_parser.add_argument(
        "--language", type=str, default="en", help="Language to use for the OCR task"
    )

    # Sub-command for getting the result
    result_parser = subparsers.add_parser(
        "result", help="Get the OCR result by specified task id."
    )
    result_parser.add_argument(
        "--task_id", type=str, help="Task Id returned by the upload command"
    )
    result_parser.add_argument(
        "--print_progress",
        default=True,
        action="store_true",
        help="Print the progress of the OCR task",
    )

    # Sub-command for running Ollama
    ollama_parser = subparsers.add_parser(
        "llm_generate", help="Run the Ollama endpoint"
    )
    ollama_parser.add_argument(
        "--prompt", type=str, required=True, help="Prompt for the Ollama model"
    )
    ollama_parser.add_argument(
        "--model",
        type=str,
        default="llama3.1",
        help="Model to use for the Ollama endpoint",
    )

    ollama_pull_parser = subparsers.add_parser(
        "llm_pull", help="Pull the latest Llama model from the Ollama API"
    )
    ollama_pull_parser.add_argument(
        "--model",
        type=str,
        default="llama3.1",
        help="Model to pull from the Ollama API",
    )

    # Sub-command for listing files
    list_files_parser = subparsers.add_parser(
        "list_files", help="List files using the selected storage profile"
    )
    list_files_parser.add_argument(
        "--storage_profile", type=str, default="default", help="Storage profile to use"
    )

    # Sub-command for loading a file
    load_file_parser = subparsers.add_parser(
        "load_file", help="Load a file using the selected storage profile"
    )
    load_file_parser.add_argument(
        "--file_name", type=str, required=True, help="Name of the file to load"
    )
    load_file_parser.add_argument(
        "--storage_profile", type=str, default="default", help="Storage profile to use"
    )

    # Sub-command for deleting a file
    delete_file_parser = subparsers.add_parser(
        "delete_file", help="Delete a file using the selected storage profile"
    )
    delete_file_parser.add_argument(
        "--file_name", type=str, required=True, help="Name of the file to delete"
    )
    delete_file_parser.add_argument(
        "--storage_profile", type=str, default="default", help="Storage profile to use"
    )

    args = parser.parse_args()

    if args.command == "ocr" or args.command == "ocr_upload":
        print(args)
        result = ocr_upload(
            args.file,
            False if args.disable_ocr_cache else args.ocr_cache,
            args.prompt,
            args.prompt_file,
            args.model,
            args.strategy,
            args.storage_profile,
            args.storage_filename,
            args.language,
        )
        if result is None:
            print("Error uploading file.")
            return
        if result.get("text"):
            print(result.get("text"))
        elif result:
            print(
                "File uploaded successfully. Task Id: "
                + result.get("task_id")
                + " Waiting for the result..."
            )
            text_result = get_result(result.get("task_id"), args.print_progress)
            if text_result:
                print(text_result)
    elif args.command == "ocr_request":
        result = ocr_request(
            args.file,
            False if args.disable_ocr_cache else args.ocr_cache,
            args.prompt,
            args.prompt_file,
            args.model,
            args.strategy,
            args.storage_profile,
            args.storage_filename,
            args.language,
        )
        if result is None:
            print("Error uploading file.")
            return
        if result.get("text"):
            print(result.get("text"))
        elif result:
            print(
                "File uploaded successfully. Task Id: "
                + result.get("task_id")
                + " Waiting for the result..."
            )
            text_result = get_result(result.get("task_id"), args.print_progress)
            if text_result:
                print(text_result)
    elif args.command == "result":
        text_result = get_result(args.task_id, args.print_progress)
        if text_result:
            print(text_result)
    elif args.command == "clear_cache":
        clear_cache()
    elif args.command == "llm_generate":
        llm_generate(args.prompt, args.model)
    elif args.command == "llm_pull":
        llm_pull(args.model)
    elif args.command == "list_files":
        list_files(args.storage_profile)
    elif args.command == "load_file":
        load_file(args.file_name, args.storage_profile)
    elif args.command == "delete_file":
        delete_file(args.file_name, args.storage_profile)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
