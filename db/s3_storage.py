import logging

import boto3
from botocore.client import Config

from config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.AWS_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME,
    config=Config(signature_version="s3v4"),
)


# Upload file
def upload_file(
    file_path: str, bucket: str = "images_bucket", object_name: str | None = None
) -> str | None:
    if object_name is None:
        object_name = file_path.split("/")[-1]

    try:
        with open(file_path, "rb") as f:
            s3_client.put_object(Bucket=bucket, Key=object_name, Body=f.read())
            public_url = (
                f"{settings.AWS_ENDPOINT_URL}/object/public/{bucket}/{object_name}"
            )
        logging.info(f"✓ Uploaded {object_name} to {bucket}")
        return public_url
    except Exception as e:
        logging.error(f"✗ Upload failed: {e}")
        return None
