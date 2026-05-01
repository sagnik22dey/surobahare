import os
import uuid
import boto3
import filetype
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "")
_REGION = os.getenv("S3_REGION", "auto")
_BUCKET = os.getenv("S3_BUCKET_NAME", "")
_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "")
_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "")

_FOLDER_MAP = {
    "image": "images",
    "video": "video",
    "audio": "audio",
    "application": "documents",
}

_ALLOWED_MIME_PREFIXES = {"image", "video", "audio", "application"}

_ALLOWED_APPLICATION_SUBTYPES = {
    "pdf",
    "msword",
    "vnd.openxmlformats-officedocument.wordprocessingml.document",
    "vnd.ms-excel",
    "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "vnd.ms-powerpoint",
    "vnd.openxmlformats-officedocument.presentationml.presentation",
    "zip",
    "x-zip-compressed",
}


def _get_client():
    return boto3.client(
        "s3",
        endpoint_url=_ENDPOINT,
        region_name=_REGION,
        aws_access_key_id=_ACCESS_KEY,
        aws_secret_access_key=_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def validate_and_detect(file_bytes: bytes, original_filename: str) -> tuple[str, str]:
    """
    Returns (mime_type, extension).
    Raises ValueError for disallowed types.
    """
    kind = filetype.guess(file_bytes)
    if kind is None:
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        mime = f"application/{ext}"
    else:
        mime = kind.mime
        ext = kind.extension

    mime_prefix = mime.split("/")[0]
    mime_subtype = mime.split("/")[1] if "/" in mime else ""

    if mime_prefix not in _ALLOWED_MIME_PREFIXES:
        raise ValueError(f"File type '{mime}' is not allowed.")

    if mime_prefix == "application" and mime_subtype not in _ALLOWED_APPLICATION_SUBTYPES:
        raise ValueError(f"Document type '{mime}' is not allowed.")

    return mime, ext


def upload_file(file_bytes: bytes, original_filename: str, content_type: str | None = None) -> str:
    """
    Uploads file_bytes to the S3 bucket.
    Returns the public URL of the uploaded object.
    """
    mime, ext = validate_and_detect(file_bytes, original_filename)
    resolved_content_type = content_type or mime

    mime_prefix = mime.split("/")[0]
    folder = _FOLDER_MAP.get(mime_prefix, "documents")

    key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    client = _get_client()
    client.put_object(
        Bucket=_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=resolved_content_type,
        ACL="public-read",
    )

    public_url = f"{_ENDPOINT}/{_BUCKET}/{key}"
    return public_url


def delete_file(public_url: str) -> None:
    """Deletes a file from the bucket given its public URL."""
    if not public_url.startswith(_ENDPOINT):
        return
    key = public_url.replace(f"{_ENDPOINT}/{_BUCKET}/", "")
    client = _get_client()
    client.delete_object(Bucket=_BUCKET, Key=key)
