from flask import request
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer, TransferConfig
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()
import os


url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


async def additional_video_data():
    # compress thumb using sharp
    # allow thumbnail uploading, visibility, description, title, schedule, category picking, comment sorting, comment visibility
    pass