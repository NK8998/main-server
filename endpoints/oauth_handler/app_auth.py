from flask import request, jsonify, make_response, redirect
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
from supabase import create_client
from .generate_user_data import generate_pfp


load_dotenv()



url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def verify_credentials():
    cookie_suid = request.cookies.get('SUID')
    data, count = supabase.table("user-info").select('*').eq('user_id', cookie_suid).execute()

    user_data = data[1]

    # Assuming you want to keep the original logic
    return jsonify({'message': "verified", 'user_data': user_data}), 200



def verify_cookie():
    cookie_scid = request.cookies.get('SCID')
    cookie_suid = request.cookies.get('SUID')
    storage_scid = request.args.get('SCID')
    storage_suid = request.args.get('SUID')

    if not cookie_scid or not cookie_suid:
        return jsonify({'redirect': True}), 200

    if cookie_scid != storage_scid or cookie_suid != storage_suid:
        return jsonify({'message': "cookie mismatch"}), 500
    data, count = supabase.table("user-info").select('*').eq('user_id', cookie_suid).execute()


    user_data = data[1]

    # Assuming you want to keep the original logic
    return jsonify({'message': "verified", 'user_data': user_data}), 200 
    

def set_cookies():  # Function name change for clarity
    cookie_scid = request.cookies.get('SCID')
    cookie_suid = request.cookies.get('SUID')

    redirect = False
    if not cookie_scid or not cookie_suid:
        redirect = True

    response_data = {
        'SCID': cookie_scid, 
        'SUID': cookie_suid,  
        'redirect': redirect
    }
    return jsonify(response_data)  # Return as JSON


async def web_app_auth():
    display_name = request.args.get('displayName')
    user_id = request.args.get('userID')
    target = request.args.get('target')
    channel_id = "UC" + user_id  
    # first check if their pfp exists 
    data, count = supabase.table("user-info").select('pfp_url').eq('user_id', user_id).execute()
    print(data[1])
    if len(data[1]) == 0:
        print('no data')
        await generate_pfp(user_id, display_name, channel_id)

    response = make_response(redirect(f"http://localhost:{target}"))
    
    # Set the cookies to expire in 30 days
    expires = datetime.now()
    expires = expires + timedelta(days=90)
    
    response.set_cookie("SUID", user_id, expires=expires, httponly=True)
    response.set_cookie("SCID", channel_id, expires=expires, httponly=True)

    return response


