from pathlib import Path

import boto3


class StorageError(Exception):
    """Raised when a file cannot be stored or retrieved."""


class LocalStorage:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        path = (self.root / key).resolve()
        if self.root.resolve() not in path.parents:
            raise StorageError("Invalid storage key")
        return path

    def save(self, data, key, content_type):
        del content_type
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def read(self, key):
        try:
            return self._path(key).read_bytes()
        except FileNotFoundError as error:
            raise StorageError("File not found") from error

    def delete(self, key):
        try:
            self._path(key).unlink()
        except FileNotFoundError:
            pass


class S3Storage:
    def __init__(self, bucket, region, endpoint_url=None):
        if not bucket:
            raise ValueError("S3_BUCKET is required when STORAGE_BACKEND=s3")
        self.bucket = bucket
        self.client = boto3.client(
            "s3", region_name=region, endpoint_url=endpoint_url
        )

    def save(self, data, key, content_type):
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
        )

    def read(self, key):
        try:
            return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
        except self.client.exceptions.NoSuchKey as error:
            raise StorageError("File not found") from error

    def delete(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=key)


def build_storage(config):
    if config["STORAGE_BACKEND"] == "s3":
        return S3Storage(
            bucket=config["S3_BUCKET"],
            region=config["S3_REGION"],
            endpoint_url=config["S3_ENDPOINT_URL"],
        )
    return LocalStorage(config["STORAGE_ROOT"])
