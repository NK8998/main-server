from flask import request, jsonify, make_response, redirect
import os
from supabase import create_client, Client
from pprint import pprint 
from dotenv import load_dotenv
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_recommended_videos():
    cookie_suid = request.cookies.get('SUID')
    print(cookie_suid)
    try:
        response = supabase.table('video-metadata').select('*').limit(20).execute()
        return jsonify(response.data), 200
    
    except Exception as e:
        pprint(e)
        return jsonify({'error': str(e)}), 500
    