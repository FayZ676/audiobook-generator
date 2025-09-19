import time
from typing import BinaryIO

import boto3


class S3Client:
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("s3", region_name=region_name)

    def upload_fileobj(self, bucket_name: str, file_name: str, file: BinaryIO):
        self.client.upload_fileobj(file, bucket_name, file_name)
        return f"s3://{bucket_name}/{file_name}"

    def list_files(self, bucket_name: str, prefix: str):
        response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        return [str(obj["Key"]) for obj in response.get("Contents", [])]

    def get_file(self, bucket_name: str, file_key: str) -> bytes:
        response = self.client.get_object(Bucket=bucket_name, Key=file_key)
        return response["Body"].read()

    def delete_file(self, bucket_name: str, file_name: str):
        self.client.delete_object(Bucket=bucket_name, Key=file_name)

    def get_file_metadata(self, bucket_name: str, file_key: str):
        response = self.client.head_object(Bucket=bucket_name, Key=file_key)
        return response

    def presigned_url(self, bucket_name: str, file_name: str):
        presigned_url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_name},
            ExpiresIn=3600,
        )

        try:
            metadata = self.get_file_metadata(bucket_name, file_name)
            last_modified = metadata["LastModified"]
            cache_bust_param = str(int(last_modified.timestamp()))
        except (KeyError, AttributeError, ValueError):
            cache_bust_param = str(int(time.time()))

        separator = "&" if "?" in presigned_url else "?"
        return f"{presigned_url}{separator}v={cache_bust_param}"
