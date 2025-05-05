import boto3
from botocore.exceptions import EndpointConnectionError, ClientError

from text_extract_api.files.storage_strategies.storage_strategy import (
    BaseStorageStrategy,
)


class AWSS3StorageStrategy(BaseStorageStrategy):
    def __init__(self, context):
        super().__init__(context)

        self.bucket_name = self.resolve_placeholder(
            context["settings"].get("bucket_name")
        )
        self.region = self.resolve_placeholder(context["settings"].get("region"))
        self.access_key = self.resolve_placeholder(
            context["settings"].get("access_key")
        )
        self.secret_access_key = self.resolve_placeholder(
            context["settings"].get("secret_access_key")
        )

        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region,
            )
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except EndpointConnectionError as e:
            raise RuntimeError(
                f"{str(e)}\n"
                "Check your AWS_REGION and AWS_S3_BUCKET_NAME environment variables."
            ) from e
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code in ("400", "403"):
                raise RuntimeError(
                    f"{str(e)}\n"
                    "Error: Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
                ) from e
            raise

    def save(self, file_name, dest_file_name, content):
        formatted_file_name = self.format_file_name(file_name, dest_file_name)

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=formatted_file_name,
                Body=content.encode("utf-8"),
            )
        except ClientError as e:
            raise RuntimeError(
                f"{str(e)}\n"
                f"Error saving file '{file_name}' as '{formatted_file_name}' to bucket '{self.bucket_name}'."
            ) from e

    def load(self, file_name):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_name)
            return response["Body"].read().decode("utf-8")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchKey":
                return None
            raise RuntimeError(
                f"{str(e)}\n"
                f"Error loading file '{file_name}' from bucket '{self.bucket_name}'."
            ) from e

    def list(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [item["Key"] for item in response.get("Contents", [])]
        except ClientError as e:
            raise RuntimeError(
                f"{str(e)}\nError listing objects in bucket '{self.bucket_name}'."
            ) from e

    def delete(self, file_name):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)
        except ClientError as e:
            raise RuntimeError(
                f"{str(e)}\n"
                f"Error deleting file '{file_name}' from bucket '{self.bucket_name}'."
            ) from e
