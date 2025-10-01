import os
import uuid

import boto3
from botocore.client import Config

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "avatars")

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

def upload_avatar(file, user_id: int):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png"]:
        raise ValueError("Invalid file type")

    file_name = f"{user_id}_{uuid.uuid4()}.{file_extension}"

    s3_client.upload_fileobj(
        file.file,
        MINIO_BUCKET,
        file_name,
        ExtraArgs={"ContentType": file.content_type}
    )

    file_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{file_name}"

    return file_url