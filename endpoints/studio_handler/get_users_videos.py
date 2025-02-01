from flask import request, jsonify, make_response, redirect
import os
from supabase import create_client, Client
from pprint import pprint 
from dotenv import load_dotenv
from server_globals.SDKs import get_supabase_client
load_dotenv()



async def get_users_videos():
    supabase = await get_supabase_client()
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
    