from flask import request, jsonify, make_response, redirect
import os
from supabase import create_client, Client
from pprint import pprint 
from dotenv import load_dotenv
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_comments():
    try:
        video_id = request.form.get('video_id')

        response = supabase.table('comments').select("*").eq('video_id', video_id).is_('parent_id', None).limit(20).execute()

        comments_arr = response.data or []

        return jsonify({'comments' : comments_arr}), 200
    
    except Exception as e:
        return jsonify({'Something went wrong when fetching': str(e)}), 500

    

    



