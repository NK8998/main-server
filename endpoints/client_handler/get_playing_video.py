from flask import request, jsonify
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
        selected_video = supabase.table('video-metadata').select("*").eq('video_id', video_id).execute()

        if not selected_video.data or not selected_video.data[0]:
            return jsonify({'message': 'no data found', 'video': None}), 200
        
        recommended_videos_response = supabase.table('video-metadata').select('*').limit(20).execute()

        recommended_videos = recommended_videos_response.data or []
        
        return jsonify({'message': 'video found', 'video':  selected_video.data[0], 'recommended': recommended_videos }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

