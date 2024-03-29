from flask import request, jsonify, make_response, redirect
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from pprint import pprint 
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_playing_video():
    video_id = request.form['videoId']
    try:
        response = supabase.table('video-metadata').select("*").eq('video_id', video_id).execute()
        if not response.data or not response.data[0]:
            return jsonify({'message': 'no data found'}), 200
        
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

