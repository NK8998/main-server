from flask import request
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import S3Transfer, TransferConfig
import os
from pprint import pprint 
from supabase import create_client
from dotenv import load_dotenv
import asyncio
import aioboto3
import json

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


async def delete_video_from_AWS(video_id):
    print(video_id)

    prefix  =f'{video_id}/'
    s3_client = boto3.resource('s3', 
                                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    unprocessed_bucket = os.getenv('AWS_S3_UNPROCESSED_BUCKET')
    processed_bucket = os.getenv('AWS_PROCESSED_BUCKET')

    # delete from original bucket
    s3_client.meta.client.delete_object(Bucket=unprocessed_bucket, Key=video_id)
    
    response = s3_client.meta.client.list_objects_v2(Bucket=processed_bucket, Prefix=prefix)

    if response.get('Contents'):
        for obj in response['Contents']:
            key = obj.get('Key')
            if key:
                print(f"Deleting {key}")
                s3_client.meta.client.delete_object(Bucket=processed_bucket, Key=key)

    print('done deleteing')




async def delete_video_from_supabase(video_id):
    print(video_id)

    try:
        data, count = supabase.table('video-metadata').delete().match({'video_id': video_id}).execute()
        return data[1][0]
    except IndexError:
        print("No data found.")
        return None




async def initiate_video_deletion():
    try:
        # ids_array = request.form.get('ids')
        ids_array = request.form.get('ids').split(',')
        
        print( ids_array)
        tasks = []

        for video_id in ids_array:
            tasks.append(delete_video_from_supabase(video_id))
            tasks.append(delete_video_from_AWS(video_id))

        await asyncio.gather(*tasks)

        return 'successfully deleted video(s)', 200

    except Exception as e :
        print(f"An error occurred: {str(e)}")
        return 'An error occurred.', 500


   