from idlelib.browser import file_open

import gradio as gr
from pathlib import Path
import requests
import json
from logging import getLogger, StreamHandler, Formatter, DEBUG
from logging.handlers import RotatingFileHandler

logger = getLogger(__name__)

root = Path(__file__).resolve().parent
log_path = root / "logs" / "uploader.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

file_handler = RotatingFileHandler(
    log_path,
    maxBytes=2_000_000,
    backupCount=5,
    encoding="utf-8"
)
file_handler.formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")

if not logger.hasHandlers():
    logger.formatter = Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                         datefmt='%m/%d/%Y %I:%M:%S %p')

    logger.addHandler(StreamHandler())
    logger.addHandler(file_handler)
    logger.setLevel(DEBUG)

logger.info(msg="Logger is set up.")


IP_ADDRESS = "127.0.0.1:8000"
TEST_IP = "127.0.0.1:8000"

TEST: bool = True
if TEST:
    address: str = f"http://{TEST_IP}/savedata/"
else:
    address: str = f"http://{IP_ADDRESS}/savedata/"


default_data_path: Path = Path(r'C:/') / 'Users' / 'avriza' / 'Desktop' / 'pyscicat'

default_thumbnail_path: Path = Path(r'C:/') / 'Users' / 'avriza' / 'Desktop' / 'pyscicat' / 'examples'

def toggle_visibility(choice):
    """
    Turns on or off visability of pathname textboxes depending on user's answer to gr.radio block.

    :param choice:
    :return:
    """
    if choice == "Default":
        return gr.update(visible=False), gr.update(visible=False)
    elif choice == "Other":
        return gr.update(visible=True), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False)

def upload(name: str,
           email: str,
           exp_date: str,
           experiment: str,
           data_file,
           thumbnail_file,
           minio_bucket: str,
           data_save_path: str = None,
           thumbnail_save_path: str = None):

    """
    Intakes user input and files before making a post request to FASTAPI back end.

    :param name:
    :param email:
    :param exp_date:
    :param experiment:
    :param data_file:
    :param thumbnail_file:
    :param minio_bucket:
    :param data_save_path:
    :param thumbnail_save_path:
    :return:
    """

    if data_save_path is None:
        data_save_path: Path = default_data_path
        logger.info(f"Default data path is used: {data_save_path}")

    else:
        logger.info(f"Custom data file path is used: {data_save_path}")

    if thumbnail_save_path is None:
        thumbnail_save_path: Path = default_thumbnail_path
        logger.info(f"Default thumbnail path is used: {data_save_path}")
    else:
        logger.info(f"Custom data thumbnail path is used: {data_save_path}")


    metadata = {
        "name": name,
        "email": email,
        "date": exp_date,
        "experiment": experiment,
        "minio_bucket": minio_bucket,
        "data_path": data_save_path,
        "thumbnail_path": thumbnail_save_path,
    }

    if thumbnail_file is None:
        files = {
            # data file
            "data_file": (
                Path(f"{data_file}").name,
                open(f"{data_file}", "rb"),
                "application/json"  # MIME type for JSON files
            )
        }

        logger.info("No thumbnail was provided.")

    else:
        files = {
            # image
            "thumbnail_file": (
                Path(f"{thumbnail_file}").name,  # filename the server will see
                open(f"{thumbnail_file}", "rb"),  # file handle (binary mode!)
                "image/png"  # MIME type
            ),

            # Data file
            "data_file": (
                Path(f"{data_file}").name,
                open(f"{data_file}", "rb"), # file handle (binary mode!)
                "application/json"  # MIME type for JSON files
            )
        }

    # r = requests.post(url=address, json=metadata, files=files)
    r = requests.post(url=address, data= {'metadata': json.dumps(metadata)}, files=files)
    r.raise_for_status()

    if r.status_code == requests.codes.ok:
        logger.info(f"File uploaded! :)\n {r.status_code}")
        return f"File uploaded! :)\n Status code: {r.status_code}"
    else:
        logger.error(f"Could not upload files! :(\n Status code: {r.status_code}")
        return f"Could not upload files! :(\n Status code: {r.status_code}"