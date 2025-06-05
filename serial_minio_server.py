import json
import os
import serial
import boto3
from botocore.client import Config

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "115200"))

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "experiments")
USE_SSL = bool(int(os.getenv("MINIO_USE_SSL", "0")))

s3_client = boto3.client(
    "s3",
    endpoint_url=f"{'https' if USE_SSL else 'http'}://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


def listen_and_upload():
    """Listen on serial port for JSON messages and upload to Minio."""
    os.makedirs("/tmp/serial_uploads", exist_ok=True)
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=10) as ser:
        while True:
            line = ser.readline()
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                print("Received invalid JSON")
                continue

            # Prepare object key
            name = data.get("name", "unknown")
            exp_date = data.get("date", "unknown_date")
            experiment = data.get("experiment", "experiment")
            key = f"{exp_date}/{experiment}_{name}.json"

            # Write data to a temporary file
            tmp_path = os.path.join("/tmp/serial_uploads", os.path.basename(key))
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            # Upload to Minio
            try:
                s3_client.upload_file(tmp_path, MINIO_BUCKET, key)
                print(f"Uploaded {key} to bucket {MINIO_BUCKET}")
            except Exception as e:
                print(f"Failed to upload {key}: {e}")


if __name__ == "__main__":
    listen_and_upload()
