# Gradio Uploader

## Project Purpose

This repository provides a simple interface for sending experimental data to a FastAPI backend and optionally registering the results in MinIO and SciCat.  The `gradio_uploader.py` script creates a small Gradio UI where a user can fill in metadata and select files to upload.  The backend defined in `flask_backend.py` accepts the upload and writes the files to disk.  Utilities in `minio_scicat_ingestion.py` show how the same files can be pushed to MinIO object storage and recorded in SciCat.

## Installation

1. Clone the repository and change into the folder.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Python 3.10+ is recommended.

## Running the Application

Start the backend first.  From the repository root run:
```bash
uvicorn flask_backend:app --reload
```
By default, this serves the API on `http://127.0.0.1:8000`.

In a separate terminal launch the Gradio interface:
```bash
python gradio_uploader.py
```
The UI will open in the browser and submit uploads to the FastAPI endpoint.

## Environment Configuration

Several values used throughout the ingestion scripts are currently hard coded.  They should be provided as environment variables instead:

| Variable           | Description                                                   |
|--------------------|---------------------------------------------------------------|
| `MINIO_SERVER`     | Hostname for the MinIO server (e.g. `localhost`).             |
| `MINIO_ACCESS_KEY` | Access key for MinIO.                                         |
| `MINIO_SECRET_KEY` | Secret key for MinIO.                                         |
| `MINIO_BUCKET`     | Bucket that will store uploaded data.                         |
| `SCICAT_URL`       | Base API URL of SciCat (e.g. `http://localhost:3000/api/v3`). |
| `SCICAT_USERNAME`  | SciCat username used to register datasets.                    |
| `SCICAT_PASSWORD`  | SciCat password used to register datasets.                    |
| `DATA_PATH`        | Directory where uploaded data files are written.              |
| `THUMBNAIL_PATH`   | Directory for saving uploaded thumbnails.                     |

Set these variables in your shell or in a `.env` file before running any scripts.  This removes the need to edit the source to change paths or credentials.
