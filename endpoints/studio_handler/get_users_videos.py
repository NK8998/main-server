from flask import request, jsonify, make_response, redirect
import os
from supabase import create_client, Client
from pprint import pprint 
from dotenv import load_dotenv
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_users_videos():
    cookie_suid = request.cookies.get('SUID')
    cookie_scid = request.cookies.get('SCID')
    print(cookie_suid)
    if not cookie_scid or not cookie_suid:
        return 'no credentials', 400
    
    try:
        response = supabase.table('video-metadata').select('*').eq('type', 'video').eq('channel_id', cookie_scid).execute()
        return jsonify(response.data), 200
    
    except Exception as e:
        pprint(e)
        return jsonify({'error': str(e)}), 500
    