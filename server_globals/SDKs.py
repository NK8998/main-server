import os
import aioboto3
from supabase import create_client, Client
from server_globals.secrets import get_secret
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client  # Install `boto3-stubs`



# Initialize Supabase Client
async def get_supabase_client() -> Client:
    """Returns an instance of the Supabase client."""
    secrets = await get_secret("hive_credentials")
    url: str = secrets.get("SUPABASE_URL")
    key: str = secrets.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase credentials are missing")

    return create_client(url, key)

from typing import Any

async def get_boto3_client(service_name: str, region_name="ap-south-1") -> Any:
    """Returns an async Boto3 resource for the given AWS service with credentials from Secrets Manager."""

    # Fetch AWS credentials from Secrets Manager
    secrets = await get_secret("hive_credentials")
    aws_access_key = secrets.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = secrets.get("AWS_SECRET_ACCESS_KEY")

    # Create an aioboto3 session
    session = aioboto3.Session()

    # Use async context manager for the resource
    async with session.client(
        service_name,
        region_name=region_name,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    ) as resource:
        return resource  # Return the resource instance

