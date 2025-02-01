from flask import request, jsonify
from pprint import pprint 
from dotenv import load_dotenv
from server_globals.SDKs import get_supabase_client
load_dotenv()

async def post_comment():
    supabase = await get_supabase_client()
    parent_id = request.form.get('parent_id')
    video_id = request.form.get('video_id')
    body = request.form.get('body')
    comment_id = request.form.get('comment_id')
    user_id = request.form.get('user_id')

    if not video_id or not comment_id or not user_id:
        return jsonify({"message": "Bad request"}), 400

    try:
        data = {
            'video_id': video_id,
            'parent_id': parent_id,
            'body': body,
            'comment_id': comment_id,
            'user_id': user_id
        }

        # Filter out None or empty values
        filtered_data = {k: v for k, v in data.items() if v != 'null'}

        pprint(filtered_data)

        supabase.table('comments').insert(filtered_data).execute()
        
        return jsonify({'message': 'Comment uploaded successfully'}), 200
    except Exception as e:
        print(f"Error inserting comment: {e}")
        return jsonify({'error': 'An error occurred while uploading the comment.'}), 500

