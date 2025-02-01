from flask import request
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import TransferConfig
import os
from pprint import pprint 
from dotenv import load_dotenv
import threading
import random
from server_globals.SDKs import get_supabase_client, get_boto3_client
from server_globals.secrets import get_secret
load_dotenv()

def validate_file(extension):

    valid_extensions= ['.mkv', '.mp4', '.flv', '.avi', '.mov', '.wmv', '.webm', '.3gp', '.3g2', '.mpeg', '.ts']

    if extension not in valid_extensions:
        return 'invalid'
    
    return 'valid'

async def get_instance_id():
    client = boto3.client(
        'autoscaling',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name='ap-south-1'
    )

    response = client.describe_auto_scaling_instances()
    instances = response['AutoScalingInstances']
    original_instance_id = os.getenv('AWS_ORIGINAL_INSTANCE_ID')
    instance_ids = [instance['InstanceId'] for instance in instances]

    # Add the original instance id to the list
    instance_ids.append(original_instance_id)

    print(instance_ids)
    # Pick a random id from the list
    random_id = random.choice(instance_ids)
    print(instance_ids, random_id)

    return random_id



async def upload_file():
    try:
        secrets = await get_secret("hive_credentials")
        # pprint(request.files)
        pprint({'formData': request.form})

        if 'video' not in request.files:
            return 'No file part in the request.', 400

        file = request.files['video']
        videoId = request.form['videoId']
        display_name = request.form['displayName']
        handle = request.form['handle']
        full_title = request.form['title']
        channel_id = request.form['channelId']
        pfp_url = request.form['pfpUrl']
        name_parts = os.path.splitext(full_title)
        extension = name_parts[1].lower()
        title = name_parts[0]

        validate_message = validate_file(extension)
        if validate_message == 'invalid':
            return 'Invalid file type.', 400

        if file:
            name = f'v{videoId}{title}'
            video_path = await get_video_info(file, name)
            await upload_video_metadata(videoId, title, channel_id, handle, display_name, pfp_url)

            await upload_to_s3(video_path, secrets['AWS_S3_UNPROCESSED_BUCKET'], videoId)
            await upload_to_supabase_queue(videoId)
            if os.path.exists(video_path):
                os.remove(video_path)
                
            return f'File {title} uploaded successfully!', 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 'An error occurred.', 500

async def get_video_info(file, name):
   # Get the absolute path to the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the absolute path to the 'videos' directory
    videos_dir = os.path.join(current_dir, 'videos')

    # Ensure 'videos' directory exists
    os.makedirs(videos_dir, exist_ok=True)

    # Create the path for the file inside the 'videos' directory
    file_path = os.path.join(videos_dir, name)

    # Save the file
    file.save(file_path)
    return file_path

async def upload_video_metadata(videoId, title, channel_id, handle, display_name, pfp_url):
    supabase = await get_supabase_client()
    data, count =  supabase.table('video-metadata').insert({"video_id": videoId, "title": title, "channel_id": channel_id, "display_name": display_name, "handle": handle, 'filename': title, 'visibility': 'Draft', 'pfp_url' : pfp_url}).execute()
    print(data)

async def upload_to_supabase_queue(videoId):
    #check if instance is indeed on
    supabase = await get_supabase_client()
    data2, count2 =  supabase.table('video-queue').insert({"video_id": videoId, "state": "unprocessed"}).execute()

    print(data2)


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            print(f"{self._filename}  {percentage}%")

async def upload_to_s3(file, bucket, videoId):
    """
    Uploads a file to an S3 bucket using the async boto3 client.

    :param file: The file to upload
    :param bucket: The S3 bucket name
    :param videoId: The object key for the file in S3
    :return: The S3 file URL if successful, otherwise False
    """
    secrets = await get_secret("hive_credentials")
    
    s3_client = await get_boto3_client('s3')

    # config = TransferConfig(
    #     use_threads=True,
    #     multipart_threshold=1024**2,
    #     multipart_chunksize=1024**2
    # )

    file_path = f"{videoId}/"

    try:
        await s3_client.upload_file(file, bucket, videoId, Callback=ProgressPercentage(file))
    except NoCredentialsError:
        print("Credentials not available")
        return False
    finally:
        await s3_client.close()  # Ensure we properly close the session

    file_url = f"{secrets['CLOUDFRONT_URL_VIDEO_DATA']}/{file_path}"
    return file_url



