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
        return [obj["Key"] for obj in response.get("Contents", [])]

    def get_file(self, bucket_name: str, file_name: str):
        response = self.client.get_object(Bucket=bucket_name, Key=file_name)
        return response["Body"].read()

    def delete_file(self, bucket_name: str, file_name: str):
        self.client.delete_object(Bucket=bucket_name, Key=file_name)
