import os
import boto3
from dotenv import load_dotenv

load_dotenv()

R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("R2_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    region_name="auto",
)


def upload_photo(file_obj, key: str, content_type: str) -> str:
    s3.upload_fileobj(
        file_obj,
        R2_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return f"{R2_PUBLIC_URL}/{key}"
