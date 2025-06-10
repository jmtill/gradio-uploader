from fastapi import FastAPI, UploadFile,File, Form, Response, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
import json
import shutil
from pathlib import Path

# from minio_scicat_ingestion import upload_and_register
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
    image_file: UploadFile = File(..., description = "An Image file (JPEG or PNG).")
):

    parsed_metadata: Metadata
    try:
        parsed_metadata: Metadata = Metadata.model_validate_json(metadata)
        print(f"Recieved metadata: {parsed_metadata.model_dump_json(indent=2)}")

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Metadata validation error: {e.errors()}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON metadata format."
        )

    # Handle data file

    data_root: Path = Path(parsed_metadata.data_path)
    image_root: Path = Path(parsed_metadata.thumbnail_path)

    try:
        data_file_path = data_root / data_file.filename  # e.g. …/mydir/report.csv
        data_file_path.parent.mkdir(parents=True, exist_ok=True)  # make …/mydir

        with open(data_file_path, "wb") as data:
            shutil.copyfileobj(data_file.file, data)
        print(f"Saved data file to local computer: {data_file_path}")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save data file: {e}"
        )

    try:
        image_file_path = image_root / image_file.filename  # e.g. …/mydir/experiment.png
        image_file_path.parent.mkdir(parents=True, exist_ok=True)  # make …/mydir

        with open(image_file_path, "wb") as image:
            shutil.copyfileobj(image_file.file, image)
        print(f"Saved data file to local computer: {image_file_path}")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save image file: {e}"
        )

    # upload_and_register(str(data_file_path), str(image_file_path))


    # ing.upload_and_register()
    return {
        "message": "Files and metadata uploaded successfully!",
        "metadata": parsed_metadata.model_dump(), # Use model_dump() to convert Pydantic model back to dict
        "data_filename": data_file.filename,
        "image_filename": image_file.filename,
        "data_file_path": data_file_path,
        "image_file_path": image_file_path
    }
