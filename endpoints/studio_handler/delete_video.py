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
    prefix  =f'{video_id}/'
    s3_client = aioboto3.resource('s3', 
                                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    unprocessed_bucket = os.getenv('AWS_S3_UNPROCESSED_BUCKET')
    processed_bucket = os.getenv('AWS_PROCESSED_BUCKET')

    buckets_array = [unprocessed_bucket, processed_bucket]

    delete_tasks = []
    for bucket in buckets_array:
        response = await s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        for object in response['Contents']:
            print('Deleting', object['Key'])
            delete_tasks.append(s3_client.delete_object(Bucket=bucket, Key=object['Key']))

    await asyncio.gather(*delete_tasks)

    
    


async def delete_video_from_supabase(video_id):

    data, count = supabase.table('video-metadata').delete().match({'video_id': video_id}).execute()

    if data and len(data) > 1:
        return data[1][0]
    else:
        return None




async def initiate_video_deletion():
    try:
        data = json.loads(request.data)
        ids_array = data['ids']
        tasks = []

        for id in ids_array:
            tasks.append(delete_video_from_supabase(id))
            tasks.append(delete_video_from_AWS(id))

        await asyncio.gather(*tasks)

        return 'successfully deleted video(s)', 200

    except Exception as e :
        print(f"An error occurred: {str(e)}")
        return 'An error occurred.', 500


   