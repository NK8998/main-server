from flask import request
import boto3
from botocore.exceptions import NoCredentialsError
import os

def upload_file():
    print(request.files)
    print(request.form)

    if 'video' not in request.files:
        return 'No file part in the request.', 400

    file = request.files['video']
    videoId = request.form['videoId']
    title = request.form['title']


    if file:
        upload_to_s3(file, os.getenv('AWS_S3_BUCKET_NAME'), videoId)
        return f'File {title} uploaded successfully!'
        

def extract_video_info():
    pass

def upload_to_supabase():
    pass

def upload_to_s3(file, bucket, videoId):

    s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    try:
        s3_client.upload_fileobj(file, bucket, videoId)
    except NoCredentialsError:
        print("Credentials not available")
        return False

    return True

