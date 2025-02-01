from flask import request, jsonify
from dotenv import load_dotenv
from server_globals.SDKs import get_supabase_client
load_dotenv()


async def get_playing_video():
    supabase = await get_supabase_client()
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

