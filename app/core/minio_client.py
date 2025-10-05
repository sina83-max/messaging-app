import os
import uuid

import boto3
from botocore.client import Config
from fastapi import HTTPException

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

LOCAL_AVATAR_DIR = "./uploads/avatars"
os.makedirs(LOCAL_AVATAR_DIR, exist_ok=True)

def upload_avatar(file, user_id: int):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png"]:
        raise ValueError("Invalid file type")

    file_name = f"{user_id}_{uuid.uuid4()}.{file_extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            MINIO_BUCKET,
            file_name,
            ExtraArgs={"ContentType": file.content_type}
        )
        file_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{file_name}"
        return file_url
    except Exception as e:
        print(f"MinIO upload failed: {e}, saving locally...")
        # Save locally as fallback
        try:
            # Ensure directory exists
            os.makedirs(LOCAL_AVATAR_DIR, exist_ok=True)

            # Reset file pointer before reading again
            file.file.seek(0)

            # Define local path and write the file
            local_path = os.path.join(LOCAL_AVATAR_DIR, file_name)
            with open(local_path, "wb") as f:
                f.write(file.file.read())

            print(f"Avatar saved locally at: {local_path}")
            return f"/uploads/avatars/{file_name}"  # relative path for static serving

        except Exception as local_err:
            print(f"Local upload failed: {local_err}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload avatar to both MinIO and local storage."
            )