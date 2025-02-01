from flask import request
import aioboto3
from dotenv import load_dotenv
import asyncio
from server_globals.SDKs import get_supabase_client
from server_globals.secrets import get_secret


load_dotenv()

async def delete_video_from_AWS(video_id):
    print(video_id)
    secrets = await get_secret('hive_credentials')
    unprocessed_bucket = secrets['AWS_S3_UNPROCESSED_BUCKET']
    processed_bucket = secrets['AWS_PROCESSED_BUCKET']
    prefix = f'{video_id}/'

    async def delete_objects(bucket_name, prefix):
        # Create a session for each bucket operation
        session = aioboto3.Session()
        async with session.resource('s3') as s3:
            bucket = await s3.Bucket(bucket_name)
            # Filter objects by prefix and delete in batch
            await bucket.objects.filter(Prefix=prefix).delete()

    # Delete objects from both unprocessed and processed buckets
    await delete_objects(unprocessed_bucket, video_id)
    await delete_objects(processed_bucket, prefix)

    print('Done deleting')





async def delete_video_from_supabase(video_id):
    print(video_id)

    supabase = await get_supabase_client()
    try:
        data, count = supabase.table('video-metadata').delete().match({'video_id': video_id}).execute()
        return data[1][0]
    except IndexError:
        print("No data found.")
        return None




async def initiate_video_deletion():
    cookie_suid = request.cookies.get('SUID')
    cookie_scid = request.cookies.get('SCID')
    # get session id

    if not cookie_scid or not cookie_suid:
        return 'no credentials', 400
    
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


   