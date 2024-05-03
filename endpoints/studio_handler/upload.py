from flask import request
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer, TransferConfig
import os
import ffmpeg
from pprint import pprint 
from supabase import create_client
from dotenv import load_dotenv
import threading
import random
load_dotenv()


url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


def validate_file(extension):

    valid_extensions= ['.mkv', '.mp4', '.flv', '.avi', '.mov', '.wmv', '.webm', '.3gp', '.3g2', '.mpeg', '.ts']

    if extension not in valid_extensions:
        return 'invalid'
    
    return 'valid'

# def categorize_transcoding_time(video_info):
#     duration = float(video_info['duration'])
#     bitrate = video_info['video_bitrate_kbps']

#     if duration < 5 * 60 and bitrate < 1500:
#         return 'short'
#     elif duration < 30 * 60 and bitrate < 3000:
#         return 'moderate'
#     else:
#         return 'long'

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
            # if video_info:
            #     pprint(video_info)
            #     # category = categorize_transcoding_time(video_info)


            # if video_info is None:
            #     return 'Failed to get video information.', 400
            await upload_video_metadata(videoId, title, channel_id, handle, display_name, pfp_url)

            await upload_to_s3(video_path, os.getenv('AWS_S3_UNPROCESSED_BUCKET'), videoId)
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

# async def get_video_info(file, name):
#    # Get the absolute path to the directory of the current script
#     current_dir = os.path.dirname(os.path.abspath(__file__))

#     # Get the absolute path to the 'videos' directory
#     videos_dir = os.path.join(current_dir, 'videos')

#     # Ensure 'videos' directory exists
#     os.makedirs(videos_dir, exist_ok=True)

#     # Create the path for the file inside the 'videos' directory
#     file_path = os.path.join(videos_dir, name)

#     # Save the file
#     file.save(file_path)
#     print(file_path)

#     try:
#         probe = ffmpeg.probe(file_path)['streams'] 

#         video_stream = next((stream for stream in probe if stream['codec_type'] == 'video'), None)
#         if video_stream is None:
#             print("No video stream found")
#             return None

#         width = video_stream['width']
#         height = video_stream['height']
#         r_frame_rate = video_stream['r_frame_rate']
#         bit_rate = video_stream['bit_rate'] if 'bit_rate' in video_stream else None
#         codec_name = video_stream['codec_name']
#         duration = video_stream['duration']

#         numerator, denominator = map(int, r_frame_rate.split('/'))
#         framerate = numerator / denominator

#         # Extract the video bitrate in kilobits per second (kbps)
#         video_bitrate_kbps = round(int(bit_rate) / 1000) if bit_rate else None

#         return {
#             'width': width,
#             'height': height,
#             'framerate': framerate,
#             'video_bitrate_kbps': video_bitrate_kbps,
#             'codec_name': codec_name,
#             'duration': duration
#         }
#     except Exception as e:
#         print("Failed to get video information:", str(e))
#         return None
#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)

async def upload_video_metadata(videoId, title, channel_id, handle, display_name, pfp_url):
    data, count =  supabase.table('video-metadata').insert({"video_id": videoId, "title": title, "channel_id": channel_id, "display_name": display_name, "handle": handle, 'filename': title, 'visibility': 'Draft', 'pfp_url' : pfp_url}).execute()
    print(data)

async def upload_to_supabase_queue(videoId):
    #check if instance is indeed on
    instance_id = await get_instance_id()
    data2, count2 =  supabase.table('video-queue').insert({"video_id": videoId, "state": "unprocessed", 'instance_id': instance_id}).execute()

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
    s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    config = TransferConfig(use_threads=True, multipart_threshold=1024**2, multipart_chunksize=1024**2)

    try:
        s3_resource.meta.client.upload_file(file, bucket, videoId, Config=config, Callback=ProgressPercentage(file))
    except NoCredentialsError:
        print("Credentials not available")
        return False

    return True


