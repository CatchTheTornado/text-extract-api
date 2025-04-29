# text-extract-api

Convert any image, PDF or Office document to Markdown *text* or JSON structured document with super-high accuracy, including tabular data, numbers or math formulas.

The API is built with FastAPI and uses Celery for asynchronous task processing. Redis is used for caching OCR results.

![hero doc extract](ocr-hero.webp)

## Features:
- **No Cloud/external dependencies** all you need: PyTorch based OCR (EasyOCR) + Ollama are shipped and configured via `docker-compose` no data is sent outside your dev/server environment,
- **PDF/Office to Markdown** conversion with very high accuracy using different OCR strategies including [llama3.2-vision](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/), [easyOCR](https://github.com/JaidedAI/EasyOCR), [minicpm-v](https://github.com/OpenBMB/MiniCPM-o?tab=readme-ov-file#minicpm-v-26), remote URL strategies including [marker-pdf](https://github.com/VikParuchuri/marker)
- **PDF/Office to JSON** conversion using Ollama supported models (eg. LLama 3.1)
- **LLM Improving OCR results** LLama is pretty good with fixing spelling and text issues in the OCR text
- **Removing PII** This tool can be used for removing Personally Identifiable Information out of document - see `examples`
- **Distributed queue processing** using [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)
- **Caching** using Redis - the OCR results can be easily cached prior to LLM processing,
- **Storage Strategies** switchable storage strategies (Google Drive, Local File System ...)
- **CLI tool** for sending tasks and processing results

## Screenshots

Converting MRI report to Markdown + JSON.

```bash
python client/cli.py ocr_upload --file examples/example-mri.pdf --prompt_file examples/example-mri-2-json-prompt.txt
```

Before running the example see [getting started](#getting-started)

![Converting MRI report to Markdown](./screenshots/example-1.png)

Converting Invoice to JSON and remove PII

```bash
python client/cli.py ocr_upload --file examples/example-invoice.pdf --prompt_file examples/example-invoice-remove-pii.txt
```

Before running the example see [getting started](#getting-started)

![Converting Invoice to JSON](./screenshots/example-2.png)

## Getting started

You might want to run the app directly on your machine for development purposes OR to use for example Apple GPUs (which are not supported by Docker at the moment).

### Prerequisites

To have it up and running please execute the following steps:

[Download and install Ollama](https://ollama.com/download)
[Download and install Docker](https://www.docker.com/products/docker-desktop/)


> ### Setting Up Ollama on a Remote Host
>
> To connect to an external Ollama instance, set the environment variable: `OLLAMA_HOST=http://address:port`, e.g.:
> ```bash
> OLLAMA_HOST=http(s)://127.0.0.1:5000
> ```
>
> If you want to disable the local Ollama model, use env `DISABLE_LOCAL_OLLAMA=1`, e.g.
> ```bash
> DISABLE_LOCAL_OLLAMA=1 make install
> ```
> **Note**: When local Ollama is disabled, ensure the required model is downloaded on the external instance.
>
> Currently, the `DISABLE_LOCAL_OLLAMA` variable cannot be used to disable Ollama in Docker. As a workaround, remove the `ollama` service from `docker-compose.yml` or `docker-compose.gpu.yml`.
>
> Support for using the variable in Docker environments will be added in a future release.


### Clone the Repository

First, clone the repository and change current directory to it:

```sh
git clone https://github.com/CatchTheTornado/text-extract-api.git
cd text-extract-api
```

### Setup with `Makefile`

Be default application create [virtual python env](https://docs.python.org/3/library/venv.html): `.venv`. You can disable this functionality on local setup by adding `DISABLE_VENV=1` before running script:

```bash
DISABLE_VENV=1 make install
```

```bash
DISABLE_VENV=1 make run
```

### Manual setup

Configure environment variables:

```bash
cp .env.localhost.example .env.localhost
```

You might want to just use the defaults - should be fine. After ENV variables are set, just execute:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
chmod +x run.sh
run.sh
```

This command will install all the dependencies - including Redis (via Docker, so it is not entirely docker free method of running `text-extract-api` anyways :)

(MAC) - Dependencies
```
brew update && brew install libmagic poppler pkg-config ghostscript ffmpeg automake autoconf
```

(Mac) - You need to startup the celery worker
```
source .venv/bin/activate && celery -A text_extract_api.celery_app worker --loglevel=info --pool=solo
```

Then you're good to go with running some CLI commands like:

```bash
python client/cli.py ocr_upload --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt
```

### Scaling the parallell processing

To have multiple tasks running at once - for concurrent processing please run the following command to start single worker process:

```bash
celery -A text_extract_api.tasks worker --loglevel=info --pool=solo & # to scale by concurrent processing please run this line as many times as many concurrent processess you want to have running
```

## Online demo

To try out the application with our hosted version you can skip the Getting started and try out the CLI tool against our cloud:

Open in the browser: <a href="https://demo.doctractor.com/">demo.doctractor.com</a>

... or run n the terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
export OCR_UPLOAD_URL=https://doctractor:Aekie2ao@api.doctractor.com/ocr/upload
export RESULT_URL=https://doctractor:Aekie2ao@api.doctractor.com/ocr/result/

python client/cli.py ocr_upload --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt
```

[Demo Source code](https://github.com/CatchTheTornado/text-extract-api-demo)

**Note:** In the free demo we don't guarantee any processing times. The API is Open so please do **not send any secret documents neither any documents containing personal information**, If you do - you're doing it on your own risk and responsiblity.

<img src="screenshots/demo.png" alt="Demo screenshot" />

## Join us on Discord

In case of any questions, help requests or just feedback - please [join us on Discord](https://discord.gg/NJzu47Ye3a)!


## Text extract strategies

### `easyocr`

Easy OCR is available on Apache based license. It's general purpose OCR with support for more than 30 languages, probably with the best performance for English.

Enabled by default. Please do use the `strategy=easyocr` CLI and URL parameters to use it.


### `minicpm-v`

MiniCPM-V is an Apache based licensed OCR strategy.

The usage of MiniCPM-o/V model weights must strictly follow [MiniCPM Model License.md](https://github.com/OpenBMB/MiniCPM/blob/main/MiniCPM%20Model%20License.md).

The models and weights of MiniCPM are completely free for academic research. After filling out a ["questionnaire"](https://modelbest.feishu.cn/share/base/form/shrcnpV5ZT9EJ6xYjh3Kx0J6v8g) for registration, are also available for free commercial use.

Enabled by default. Please do use the `strategy=minicpm_v` CLI and URL parameters to use it.

| ⚠️ **Remember to pull the model in Ollama first**       |
|---------------------------------------------------------|
| You need to pull the model in Ollama - use the command: |
| `python client/cli.py llm_pull --model minicpm-v`       |
| Or, if you have Ollama locally: `ollama pull minicpm-v` |



### `llama_vision`

LLama 3.2 Vision Strategy is licensed on [Meta Community License Agreement](https://ollama.com/library/llama3.2-vision/blobs/0b4284c1f870). Works great for many languages, although due to the number of parameters (90b) this model is probably **the slowest** one.

Enabled by default. Please do use the `strategy=llama_vision` CLI and URL parameters to use it. It's by the way the default strategy


### `remote`

Some OCR's - like [Marker, state of the art PDF OCR](https://github.com/VikParuchuri/marker) - works really great for more than 50 languages, including great accuracy for Polish and other languages - let's say that are "diffult" to read for standard OCR.

The `marker-pdf` is however licensed on GPL3 license and **therefore it's not included** by default in this application (as we're bound to MIT).

The weights for the models are licensed cc-by-nc-sa-4.0, but I will waive that for any organization under $5M USD in gross revenue in the most recent 12-month period AND under $5M in lifetime VC/angel funding raised. You also must not be competitive with the Datalab API. If you want to remove the GPL license requirements (dual-license) and/or use the weights commercially over the revenue limit, check out the options here.

To have it up and running you can execute the following steps:

```bash
mkdir marker-distribution # this should be outside of the `text-extract-api` folder!
cd marker-distribution
pip install marker-pdf
pip install -U uvicorn fastapi python-multipart
marker_server --port 8002
```

Set the Remote API Url:

**Note: *** you might run `marker_server` on different port or server - then just make sure you export a proper env setting beffore starting off `text-extract-api` server:

```bash
export REMOTE_API_URL=http://localhost:8002/marker/upload
```

**Note: *** the URL might be also set via `/config/strategies.yaml` file

Run the `text-extract-api`:

```bash
make run
```

Please do use the `strategy=remote` CLI and URL parameters to use it. For example:

```bash
curl -X POST -H "Content-Type: multipart/form-data" -F "file=@examples/example-mri.pdf" -F "strategy=remote" -F "ocr_cache=true" -F "prompt=" -F "model=" "http://localhost:8000/ocr/upload"
```

We are connecting to remote OCR via it's API to not share the same license (GPL3) by having it all linked on the source code level.

## Getting started with Docker

### Prerequisites

- Docker
- Docker Compose

### Clone the Repository

```sh
git clone https://github.com/CatchTheTornado/text-extract-api.git
cd text-extract-api
```

### Using `Makefile`
You can use the `make install` and `make run` commands to set up the Docker environment for `text-extract-api`. You can find the manual steps required to do so described below.


### Manual setup

Create `.env` file in the root directory and set the necessary environment variables. You can use the `.env.example` file as a template:

```bash
# defaults for docker instances
cp .env.example .env
```

or

```bash
# defaults for local run
cp .env.example.localhost .env
```

Then modify the variables inside the file:

```bash
#APP_ENV=production # sets the app into prod mode, otherwise dev mode with auto-reload on code changes
REDIS_CACHE_URL=redis://localhost:6379/1
STORAGE_PROFILE_PATH=./storage_profiles
LLAMA_VISION_PROMPT="You are OCR. Convert image to markdown."

# CLI settings
OCR_URL=http://localhost:8000/ocr/upload
OCR_UPLOAD_URL=http://localhost:8000/ocr/upload
OCR_REQUEST_URL=http://localhost:8000/ocr/request
RESULT_URL=http://localhost:8000/ocr/result/
CLEAR_CACHE_URL=http://localhost:8000/ocr/clear_cache
LLM_PULL_API_URL=http://localhost:8000/llm_pull
LLM_GENERATE_API_URL=http://localhost:8000/llm_generate

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
OLLAMA_HOST=http://localhost:11434
APP_ENV=development  # Default to development mode
```


**Note:** In order to properly save the output files, you might need to modify `storage_profiles/default.yaml` to change the default storage path according to the volumes path defined in the `docker-compose.yml`

### Build and Run the Docker Containers

Build and run the Docker containers using Docker Compose:

```bash
docker-compose up --build
```

... for GPU support run:

```bash
docker-compose -f docker-compose.gpu.yml -p text-extract-api-gpu up --build
```

**Note:** While on Mac - Docker does not support Apple GPUs. In this case you might want to run the application natively without the Docker Compose please check [how to run it natively with GPU support](#getting-started)


This will start the following services:
 - **FastAPI App**: Runs the FastAPI application.
 - **Celery Worker**: Processes asynchronous OCR tasks.
 - **Redis**: Caches OCR results.
 - **Ollama**: Runs the Ollama model.

## Cloud - paid edition

If the on-prem is too much hassle [ask us about the hosted/cloud edition](mailto:info@catchthetornado.com?subject=text-extract-api%20but%20hosted) of text-extract-api, we can setup it you, billed just for the usage.

## CLI tool

**Note**: While on Mac, you may need to create a virtual Python environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
# now you've got access to `python` and `pip` within your virutal env.
pip install -e . # install main project requirements
```


The project includes a CLI for interacting with the API. To make it work, first run:

```bash
cd client
pip install -e .
```


### Pull the LLama3.1 and LLama3.2-vision models

You might want to test out [different models supported by LLama](https://ollama.com/library)

```bash
python client/cli.py llm_pull --model llama3.1
python client/cli.py llm_pull --model llama3.2-vision
```

These models are required for most features supported by `text-extract-api`.


### Upload a File for OCR (converting to Markdown)

```bash
python client/cli.py ocr_upload --file examples/example-mri.pdf --ocr_cache
```

or alternatively

```bash
python client/cli.py ocr_request --file examples/example-mri.pdf --ocr_cache
```

The difference is just that the first call uses `ocr/upload` - multipart form data upload, and the second one is a request to `ocr/request` sending the file via base64 encoded JSON property - probable a better suit for smaller files.


### Upload a File for OCR (processing by LLM)

**Important note:** To use LLM you must first run the **llm_pull** to get the specific model required by your requests.

For example, you must run:

```bash
python client/cli.py llm_pull --model llama3.1
python client/cli.py llm_pull --model llama3.2-vision
```

and only after to run this specific prompt query:

```bash
python client/cli.py ocr_upload --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt --language en
```

**Note:** The language argument is used for the OCR strategy to load the model weights for the selected language. You can specify multiple languages as a list: `en,de,pl` etc.

The `ocr` command can store the results using the `storage_profiles`:
  - **storage_profile**: Used to save the result - the `default` profile (`./storage_profiles/default.yaml`) is used by default; if empty file is not saved
  - **storage_filename**: Outputting filename - relative path of the `root_path` set in the storage profile - by default a relative path to `/storage` folder; can use placeholders for dynamic formatting: `{file_name}`, `{file_extension}`, `{Y}`, `{mm}`, `{dd}` - for date formatting, `{HH}`, `{MM}`, `{SS}` - for time formatting


### Upload a File for OCR (processing by LLM), store result on disk

```bash
python client/cli.py ocr_upload --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt  --storage_filename "invoices/{Y}/{file_name}-{Y}-{mm}-{dd}.md"
```

### Get OCR Result by Task ID

```bash
python client/cli.py result --task_id {your_task_id_from_upload_step}
```

### List file results archived by `storage_profile`

```bash
python client/cli.py list_files
```

to use specific (in this case `google drive`) storage profile run:

```bash
python client/cli.py list_files  --storage_profile gdrive
```

### Load file result archived by `storage_profile`

```bash
python client/cli.py load_file --file_name "invoices/2024/example-invoice-2024-10-31-16-33.md"
```

### Delete file result archived by `storage_profile`

```bash
python client/cli.py delete_file --file_name "invoices/2024/example-invoice-2024-10-31-16-33.md" --storage_profile gdrive
```

or for default profile (local file system):

```bash
python client/cli.py delete_file --file_name "invoices/2024/example-invoice-2024-10-31-16-33.md"
```

### Clear OCR Cache

```bash
python client/cli.py clear_cache
```

### Test LLama

```bash
python llm_generate --prompt "Your prompt here"
```

## API Clients

You might want to use the dedicated API clients to use `text-extract-api`.

### Typescript

There's a dedicated API client for Typescript - [text-extract-api-client](https://github.com/CatchTheTornado/text-extract-api-client) and the `npm` package by the same name:

```bash
npm install text-extract-api-client
```

Usage:

```js
import { ApiClient, OcrRequest } from 'text-extract-api-client';
const apiClient = new ApiClient('https://api.doctractor.com/', 'doctractor', 'Aekie2ao');
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('prompt', 'Convert file to JSON and return only JSON'); // if not provided, no LLM transformation will gonna happen - just the OCR
formData.append('strategy', 'llama_vision');
formData.append('model', 'llama3.1');
formData.append('ocr_cache', 'true');

apiClient.uploadFile(formData).then(response => {
    console.log(response);
});
```

## Endpoints

### OCR Endpoint via File Upload / multiform data
- **URL**: /ocr/upload
- **Method**: POST
- **Parameters**:
  - **file**: PDF, image or Office file to be processed.
  - **strategy**: OCR strategy to use (`llama_vision`, `minicpm_v`, `remote` or `easyocr`). See the [available strategies](#text-extract-stratgies)
  - **ocr_cache**: Whether to cache the OCR result (true or false).
  - **prompt**: When provided, will be used for Ollama processing the OCR result
  - **model**: When provided along with the prompt - this model will be used for LLM processing
  - **storage_profile**: Used to save the result - the `default` profile (`./storage_profiles/default.yaml`) is used by default; if empty file is not saved
  - **storage_filename**: Outputting filename - relative path of the `root_path` set in the storage profile - by default a relative path to `/storage` folder; can use placeholders for dynamic formatting: `{file_name}`, `{file_extension}`, `{Y}`, `{mm}`, `{dd}` - for date formatting, `{HH}`, `{MM}`, `{SS}` - for time formatting
  - **language**: One or many (`en` or `en,pl,de`) language codes for the OCR to load the language weights

Example:

```bash
curl -X POST -H "Content-Type: multipart/form-data" -F "file=@examples/example-mri.pdf" -F "strategy=easyocr" -F "ocr_cache=true" -F "prompt=" -F "model=" "http://localhost:8000/ocr/upload"
```

### OCR Endpoint via JSON request
- **URL**: /ocr/request
- **Method**: POST
- **Parameters** (JSON body):
  - **file**: Base64 encoded PDF file content.
  - **strategy**: OCR strategy to use (`llama_vision`, `minicpm_v`, `remote` or `easyocr`). See the [available strategies](#text-extract-stratgies)
  - **ocr_cache**: Whether to cache the OCR result (true or false).
  - **prompt**: When provided, will be used for Ollama processing the OCR result.
  - **model**: When provided along with the prompt - this model will be used for LLM processing.
  - **storage_profile**: Used to save the result - the `default` profile (`/storage_profiles/default.yaml`) is used by default; if empty file is not saved.
  - **storage_filename**: Outputting filename - relative path of the `root_path` set in the storage profile - by default a relative path to `/storage` folder; can use placeholders for dynamic formatting: `{file_name}`, `{file_extension}`, `{Y}`, `{mm}`, `{dd}` - for date formatting, `{HH}`, `{MM}`, `{SS}` - for time formatting.
  - **language**: One or many (`en` or `en,pl,de`) language codes for the OCR to load the language weights

Example:

```bash
curl -X POST "http://localhost:8000/ocr/request" -H "Content-Type: application/json" -d '{
  "file": "<base64-encoded-file-content>",
  "strategy": "easyocr",
  "ocr_cache": true,
  "prompt": "",
  "model": "llama3.1",
  "storage_profile": "default",
  "storage_filename": "example.md"
}'
```

### OCR Result Endpoint
- **URL**: /ocr/result/{task_id}
- **Method**: GET
- **Parameters**:
  - **task_id**: Task ID returned by the OCR endpoint.

Example:

```bash
curl -X GET "http://localhost:8000/ocr/result/{task_id}"
```

### Clear OCR Cache Endpoint
 - **URL**: /ocr/clear_cache
 - **Method**: POST

Example:
```bash
curl -X POST "http://localhost:8000/ocr/clear_cache"
```


### Ollama Pull Endpoint
- **URL**: /llm/pull
- **Method**: POST
- **Parameters**:
  - **model**: Pull the model you are to use first

Example:

```bash
curl -X POST "http://localhost:8000/llm/pull" -H "Content-Type: application/json" -d '{"model": "llama3.1"}'
```

### Ollama Endpoint
- **URL**: /llm/generate
- **Method**: POST
- **Parameters**:
  - **prompt**: Prompt for the Ollama model.
  - **model**: Model you like to query

Example:

```bash
curl -X POST "http://localhost:8000/llm/generate" -H "Content-Type: application/json" -d '{"prompt": "Your prompt here", "model":"llama3.1"}'
```

### List storage files:

- **URL:** /storage/list
- **Method:** GET
- **Parameters**:
  - **storage_profile**: Name of the storage profile to use for listing files (default: `default`).

### Download storage file:

- **URL:** /storage/load
- **Method:** GET
- **Parameters**:
  - **file_name**: File name to load from the storage
  - **storage_profile**: Name of the storage profile to use for listing files (default: `default`).

### Delete storage file:

- **URL:** /storage/delete
- **Method:** DELETE
- **Parameters**:
  - **file_name**: File name to load from the storage
  - **storage_profile**: Name of the storage profile to use for listing files (default: `default`).


## Storage profiles

The tool can automatically save the results using different storage strategies and storage profiles. Storage profiles are set in the `/storage_profiles` by a yaml configuration files.

### Local File System

```yaml
strategy: local_filesystem
settings:
  root_path: /storage # The root path where the files will be stored - mount a proper folder in the docker file to match it
  subfolder_names_format: "" # eg: by_months/{Y}-{mm}/
  create_subfolders: true
```

### Google Drive

```yaml
strategy: google_drive
settings:
## how to enable GDrive API: https://developers.google.com/drive/api/quickstart/python?hl=pl

  service_account_file: /storage/client_secret_269403342997-290pbjjlb06nbof78sjaj7qrqeakp3t0.apps.googleusercontent.com.json
  folder_id:
```

Where the `service_account_file` is a `json` file with authorization credentials. Please read on how to enable Google Drive API and prepare this authorization file [here](https://developers.google.com/drive/api/quickstart/python?hl=pl).

Note: Service Account is different account that the one you're using for Google workspace (files will not be visible in the UI)

### Amazon S3 - Cloud Object Storage

```yaml
strategy: aws_s3
settings:
  bucket_name: ${AWS_S3_BUCKET_NAME}
  region: ${AWS_REGION}
  access_key: ${AWS_ACCESS_KEY_ID}
  secret_access_key: ${AWS_SECRET_ACCESS_KEY}
```

#### Requirements for AWS S3 Access Key

1. **Access Key Ownership**
   The access key must belong to an IAM user or role with permissions for S3 operations.

2. **IAM Policy Example**
   The IAM policy attached to the user or role must allow the necessary actions. Below is an example of a policy granting access to an S3 bucket:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:ListBucket",
                   "s3:DeleteObject"
               ],
               "Resource": [
                   "arn:aws:s3:::your-bucket-name",
                   "arn:aws:s3:::your-bucket-name/*"
               ]
           }
       ]
   }
   ```

Next, populate the appropriate `.env` file (e.g., .env, .env.localhost) with the required AWS credentials:

```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=your-region
AWS_S3_BUCKET_NAME=your-bucket-name
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
In case of any questions please contact us at: info@catchthetornado.com
