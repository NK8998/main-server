from flask import request, jsonify
from dotenv import load_dotenv
from server_globals.SDKs import get_supabase_client
load_dotenv()

async def get_comments():
    supabase = await get_supabase_client()
    try:
        video_id = request.form.get('video_id')

        response = supabase.table('comments').select("*").eq('video_id', video_id).is_('parent_id', None).limit(20).execute()

        comments_arr = response.data or []

        return jsonify({'comments' : comments_arr}), 200
    
    except Exception as e:
        return jsonify({'Something went wrong when fetching': str(e)}), 500

    

    



