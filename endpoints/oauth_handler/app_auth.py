from flask import request, jsonify, make_response, redirect
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
import subprocess
import os
import asyncio
import random
import colorsys
from dotenv import load_dotenv
from supabase import create_client
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer, TransferConfig
import boto3
from pprint import pprint 
import ffmpeg



load_dotenv()



url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def verify_credentials():
    cookie_suid = request.cookies.get('SUID')
    data, count = supabase.table("user-info").select('*').eq('user_id', cookie_suid).execute()

    user_data = data[1]

    # Assuming you want to keep the original logic
    return jsonify({'message': "verified", 'user_data': user_data}), 200



def verify_cookie():
    cookie_scid = request.cookies.get('SCID')
    cookie_suid = request.cookies.get('SUID')
    storage_scid = request.args.get('SCID')
    storage_suid = request.args.get('SUID')

    if not cookie_scid or not cookie_suid:
        return jsonify({'redirect': True}), 200

    if cookie_scid != storage_scid or cookie_suid != storage_suid:
        return jsonify({'message': "cookie mismatch"}), 500
    data, count = supabase.table("user-info").select('*').eq('user_id', cookie_suid).execute()


    user_data = data[1]

    # Assuming you want to keep the original logic
    return jsonify({'message': "verified", 'user_data': user_data}), 200 
    

def set_cookies():  # Function name change for clarity
    cookie_scid = request.cookies.get('SCID')
    cookie_suid = request.cookies.get('SUID')

    redirect = False
    if not cookie_scid or not cookie_suid:
        redirect = True

    response_data = {
        'SCID': cookie_scid, 
        'SUID': cookie_suid,  
        'redirect': redirect
    }
    return jsonify(response_data)  # Return as JSON


async def web_app_auth():
    display_name = request.args.get('displayName')
    user_id = request.args.get('userID')
    target = request.args.get('target')
    channel_id = "UC" + user_id  
    # first check if their pfp exists 
    data, count = supabase.table("user-info").select('pfp_url').eq('user_id', user_id).execute()
    print(data[1])
    if len(data[1]) == 0:
        print('no data')
        await generate_pfp(user_id, display_name, channel_id)

    response = make_response(redirect(f"http://localhost:{target}"))
    
    # Set the cookies to expire in 30 days
    expires = datetime.now()
    expires = expires + timedelta(days=90)
    
    response.set_cookie("SUID", user_id, expires=expires, httponly=True)
    response.set_cookie("SCID", channel_id, expires=expires, httponly=True)

    return response




def hsl_to_hex(h, s, l):
    # Convert HSL color to RGB
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    
    # Convert RGB color to hexadecimal and return
    return '{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))


async def generate_pfp(user_id, display_name, channel_id):
    # Define the command
    letter = display_name[0]
    number = random.randint(0, 359)
    hex = hsl_to_hex(number, 80, 52)
    
  
    script_directory = os.path.dirname(os.path.realpath(__file__))
        # Change the working directory
    os.chdir(script_directory)

    command = [
    "ffmpeg", "-loglevel", "debug", "-f", "lavfi", "-i", f"color=c=0x{hex}:s=88x88:d=5", "-vf",
    f"[in]drawtext=fontfile=./_font/RobotoFlex-Regular.ttf:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text={letter}[out]",
    "-frames:v", "1", f"{user_id}.png"
    ]

    # Run the command

    process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()

    # Check if the command was successful
    if process.returncode != 0:
        print(f"Error executing command: {stderr.decode()}")
    else:
        print("Command executed successfully")
        file = f"./{user_id}.png"
        file_name = f"{user_id}.png"
        bucket = os.getenv('AWS_S3_USER_DATA_BUCKET')
        pfp_url = await upload_to_s3(file, bucket, user_id, file_name)
        os.remove(file)
        await upload_to_supabase(user_id, channel_id, pfp_url, display_name)

async def upload_to_s3(file, bucket, user_id, file_name):
    s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    config = TransferConfig(use_threads=True, multipart_threshold=1024**2, multipart_chunksize=1024**2)

    file_path = f"{user_id}/{file_name}"

    try:
        s3_resource.meta.client.upload_file(file, bucket, file_path, Config=config)
    except NoCredentialsError:
        print("Credentials not available")
        return None

    # Generate the URL of the uploaded file
    file_url = f"{os.getenv('CLOUDFRONT_URL')}/{user_id}/{file_name}"

    return file_url


async def upload_to_supabase(user_id, channel_id, pfp_url, display_name):
    supabase.table('user-info').insert({'user_id': user_id, 'channel_id': channel_id, 'pfp_url': pfp_url, 'display_name': display_name, 'handle': f'@{display_name}' }).execute()
    pass

