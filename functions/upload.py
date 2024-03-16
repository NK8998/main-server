from flask import request
import boto3
from botocore.exceptions import NoCredentialsError
import os
import ffmpeg
from pprint import pprint 
from supabase import create_client
from dotenv import load_dotenv
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


async def upload_file():
    try:
        # pprint(request.files)
        pprint({'formData': request.form})

        if 'video' not in request.files:
            return 'No file part in the request.', 400

        file = request.files['video']
        videoId = request.form['videoId']
        title = request.form['title']
        channelId = request.form['channelId']

        extension = os.path.splitext(title)[1]

        validate_message = validate_file(extension)
        if validate_message == 'invalid':
            return 'Invalid file type.', 400

        if file:
            # name = f'v{videoId}{title}'
            # video_info = await get_video_info(file, name)
            # if video_info:
            #     pprint(video_info)
            #     # category = categorize_transcoding_time(video_info)


            # if video_info is None:
            #     return 'Failed to get video information.', 400
            await upload_to_supabase(videoId, title, channelId)
            await upload_to_s3(file, os.getenv('AWS_S3_UNPROCESSED_BUCKET'), videoId)
            return f'File {title} uploaded successfully!'
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 'An error occurred.', 500
        

# async def get_video_info(file, name):
#    # Get the absolute path to the directory of the current script
#     current_dir = os.path.dirname(os.path.abspath(__file__))

#     # Get the absolute path to the 'uploads' directory
#     uploads_dir = os.path.join(current_dir, 'uploads')

#     # Ensure 'uploads' directory exists
#     os.makedirs(uploads_dir, exist_ok=True)

#     # Create the path for the file inside the 'uploads' directory
#     file_path = os.path.join(uploads_dir, name)

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

async def upload_to_supabase(videoId, title, channelId):
    data, count =  supabase.table('video-metadata').insert({"video_id": videoId, "title": title, "channel_id": channelId}).execute()
    data2, count2 =  supabase.table('video-queue').insert({"video_id": videoId}).execute()

    print(data2)

async def upload_to_s3(file, bucket, videoId):

    s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    try:
        s3_client.upload_fileobj(file, bucket, videoId)
    except NoCredentialsError:
        print("Credentials not available")
        return False

    return True

