from fastapi import FastAPI, UploadFile,File, Form, Response, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
import json
import shutil
from pathlib import Path
from logging import getLogger, StreamHandler, Formatter, DEBUG
from logging.handlers import RotatingFileHandler

# from minio_scicat_ingestion import upload_and_register

logger = getLogger(__name__)

root = Path(__file__).resolve().parent
log_path = root / "logs" / "backend.log"
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

logger.info("Logger is set up.")

app = FastAPI()

class Metadata(BaseModel):
    name: str = Field(..., description="Name of user who ran the experiment.")
    email: str = Field(..., description="Email of user who ran the experiment.")
    date: str = Field(..., description="Date the experiment was run.")
    experiment: str = Field(..., description="Name of the experiment.")
    minio_bucket: str = Field(..., description="Minio bucket of the experiment.")
    data_path: str = Field(..., description="Path where experiment data will be saved.")
    thumbnail_path: str = Field(..., description="Path where thumbnail will be saved.")

@app.get("/")
async def greet():
    return {"message": "Hello World"}

@app.post("/savedata/")
async def save_data(
    metadata: str = Form(..., description="JSON metdata string.")
        ,
    data_file: UploadFile = File(..., description = "A JSON or CSV file.")
        ,
    thumbnail_file: UploadFile = File(..., description ="An Image file (JPEG or PNG).")
):

    parsed_metadata: Metadata
    try:
        parsed_metadata: Metadata = Metadata.model_validate_json(metadata)

        logger.info(f"Recieved metadata: {parsed_metadata.model_dump_json(indent=2)}")

    except ValidationError as e:
        logger.error("Could not validate metadata!", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Metadata validation error: {e.errors()}"
        )
    except json.JSONDecodeError as e:
        logger.error("Could not decode JSON!", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON metadata format: {e}."
        )

    # Handle data file
    data_root: Path = Path(parsed_metadata.data_path)
    logger.info(f"Recieved data root: {data_root.resolve()}")

    thumbnail_root: Path = Path(parsed_metadata.thumbnail_path)
    logger.info(f"Recieved image root: {thumbnail_root.resolve()}")


    try:
        data_file_path = data_root / data_file.filename  # e.g. …/mydir/report.csv
        data_file_path.parent.mkdir(parents=True, exist_ok=True)  # make …/mydir
        logger.info(f"data file path created: {data_file_path}")

        with open(data_file_path, "wb") as data:
            shutil.copyfileobj(data_file.file, data)
        logger.info(f"Saved data file to local computer: {data_file_path}")

    except Exception as e:
        logger.error("Data file could not be saved to local computer!", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save data file: {e}"
        )

    try:
        thumbnail_file_path = (thumbnail_root / thumbnail_file.filename)  # e.g. …/mydir/experiment.png
        thumbnail_file_path.parent.mkdir(parents=True, exist_ok=True)  # make …/mydir
        logger.info(f"Image file path created: {thumbnail_file_path}")


        with open(thumbnail_file_path, "wb") as thumbnail:
            shutil.copyfileobj(thumbnail_file.file, thumbnail)
        logger.info(f"Saved image file to local computer: {thumbnail_file_path}")

    except Exception as e:
        logger.error("Image file could not be saved to local computer!", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save thumbnail file: {e}"
        )

    # upload_and_register(str(data_file_path), str(thumbnail_file_path))
    # logger.info("Files and metadata uploaded successfully been registered to Scicat and saved to Minio!)

    return {
        "message": "Files and metadata uploaded successfully!",
        "metadata": parsed_metadata.model_dump(), # Use model_dump() to convert Pydantic model back to dict
        "data_filename": data_file.filename,
        "thumbnail_filename": thumbnail_file.filename,
        "data_file_path": data_file_path,
        "thumbnail_file_path": thumbnail_file_path
    }
