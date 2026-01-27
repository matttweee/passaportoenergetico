from __future__ import annotations

import boto3
from botocore.config import Config

from app.storage.base import Storage


class S3Storage(Storage):
    def __init__(
        self,
        bucket: str,
        region: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str | None = None,
    ):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            config=Config(signature_version="s3v4"),
        )

    def save_bytes(self, data: bytes, storage_path: str, mime: str) -> str:
        key = storage_path.lstrip("/")
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=mime)
        return storage_path

    def read_bytes(self, storage_path: str) -> bytes:
        key = storage_path.lstrip("/")
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def get_presigned_put_url(self, storage_path: str, mime: str, expires_seconds: int = 900) -> str:
        key = storage_path.lstrip("/")
        return self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": mime},
            ExpiresIn=expires_seconds,
        )

