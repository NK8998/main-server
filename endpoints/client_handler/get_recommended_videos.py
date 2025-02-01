from flask import request, jsonify
from pprint import pprint 
from dotenv import load_dotenv
from server_globals.SDKs import get_supabase_client
load_dotenv()

async def get_recommended_videos():
    supabase = await get_supabase_client()
    cookie_suid = request.cookies.get('SUID')
    print(cookie_suid)
    try:
        response = supabase.table('video-metadata').select('*').limit(20).execute()
        return jsonify(response.data), 200
    
    except Exception as e:
        pprint(e)
        return jsonify({'error': str(e)}), 500
    