import pathlib
import sys
import multiprocessing

from celery import Celery
from dotenv import load_dotenv

sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve()))

load_dotenv(".env")


multiprocessing.set_start_method("spawn", force=True)

app = Celery(
    "text_extract_api", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)
app.config_from_object({"worker_max_memory_per_child": 8200000})

app.autodiscover_tasks(["text_extract_api.extract"], "tasks", True)
