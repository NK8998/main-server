from flask import request
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer, TransferConfig
from supabase import create_client
from dotenv import load_dotenv
import uuid
from .compress_thumb import compress_thumb
load_dotenv()
import os


url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def validate_file(extension):

    valid_extensions= ['.webp', '.jpg', '.jpeg', '.png', '.bmp', '.heic', '.heif']

    if extension not in valid_extensions:
        return 'invalid'
    
    return 'valid'


async def move_thumb(file, name):
    # Get the absolute path to the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the absolute path to the 'videos' directory
    videos_dir = os.path.join(current_dir, 'images')

    # Ensure 'videos' directory exists
    os.makedirs(videos_dir, exist_ok=True)

    # Create the path for the file inside the 'videos' directory
    file_path = os.path.join(videos_dir, name)

    # Save the file
    file.save(file_path)
    return file_path

async def upload_to_s3(file, bucket, videoId, ):
    s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    config = TransferConfig(use_threads=True, multipart_threshold=1024**2, multipart_chunksize=1024**2)

    file_path = f"{videoId}/preferredThumbnail/thumbnail.jpg"

    try:
        s3_resource.meta.client.upload_file(file, bucket, file_path, Config=config)
    except NoCredentialsError:
        print("Credentials not available")
        return False
    file_url = f"{os.getenv('CLOUDFRONT_URL_VIDEO_DATA')}/{file_path}"

    return file_url


async def upload_to_supabase(file_url, video_id):
    data, count = supabase.table('video-metadata').update({'preferred_thumbnail_url': file_url}).eq('video_id', video_id).execute()
    print(data)

async def additional_video_data():
    try:
        print('reached')
        file = request.files['thumbnail']
        full_title = request.form['title']
        video_id = request.form['videoId']
        name_parts = os.path.splitext(full_title)
        extension = name_parts[1].lower()
        # Generate a random UUID
        random_id = uuid.uuid4()

        # Convert the UUID to a string and remove hyphens to make it suitable for use as a file ID
        random_id_str = str(random_id).replace("-", "")

        validate_message = validate_file(extension)
        if validate_message == 'invalid':
            return 'Invalid file type.', 400

        if file:
            img_path = await move_thumb(file, random_id_str)
            compress_thumb_path = await compress_thumb(img_path, random_id_str)
            os.remove(img_path)
            bucket = os.getenv('AWS_PROCESSED_BUCKET')
            file_url = await upload_to_s3(compress_thumb_path, bucket, video_id)
            await upload_to_supabase(file_url, video_id)

        return 'additional data saved', 200

    except Exception as e:
        # Handle the error here
        print("An error occurred:", str(e))
        return 'Internal server error', 500



    # compress thumb using pillow
    # allow thumbnail uploading, visibility, description, title, schedule, category picking, comment sorting, comment visibility
    

