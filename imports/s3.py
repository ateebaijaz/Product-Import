import os
import boto3
from botocore.client import Config
from datetime import timedelta


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"}  # forces regional URL
        ),
    )


def generate_presigned_upload_url(object_key, expires_in=900):
    """
    Generate a presigned URL for uploading a CSV directly to S3.
    """
    s3 = get_s3_client()
    bucket = os.getenv("AWS_S3_BUCKET_NAME")

    return s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket,
            "Key": object_key,
        },
        ExpiresIn=expires_in,  # seconds
    )
