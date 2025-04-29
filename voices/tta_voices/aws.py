import boto3


class DynamoDBClient:
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("dynamodb", region_name=region_name)

    def get_items(self, table_name: str, filter_expression: str | None = None):
        if filter_expression:
            response = self.client.scan(
                TableName=table_name, FilterExpression=filter_expression
            )
        else:
            response = self.client.scan(TableName=table_name)
        return response.get("Items", [])

    def get_item(self, table_name: str, key: dict):
        response = self.client.get_item(TableName=table_name, Key=key)
        return response.get("Item")

    def put_item(self, table_name: str, item: dict):
        self.client.put_item(TableName=table_name, Item=item)


class S3Client:
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("s3", region_name=region_name)

    def upload_file(self, bucket_name: str, file_name: str, object_name: str):
        self.client.upload_file(file_name, bucket_name, object_name)

    def get_files(self, bucket_name: str):
        response = self.client.list_objects_v2(Bucket=bucket_name)
        return [obj["Key"] for obj in response.get("Contents", [])]
