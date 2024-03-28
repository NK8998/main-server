from flask import request, jsonify, make_response, redirect
from datetime import datetime, timedelta

def verify_cookie():
    cookie_scid = request.cookies.get('SCID')
    cookie_suid = request.cookies.get('SUID')
    storage_scid = request.args.get('SCID')
    storage_suid = request.args.get('SUID')

    if not cookie_scid or not cookie_suid:
        return jsonify({'redirect': True}), 200

    if cookie_scid != storage_scid or cookie_suid != storage_suid:
        return jsonify({'message': "cookie mismatch"}), 500

    # Assuming you want to keep the original logic
    return jsonify({'message': "verified"}), 200 
    

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


def web_app_auth():
    user_id = request.args.get('userID')
    target = request.args.get('target')
    channel_id = "UC" + user_id  

    response = make_response(redirect(f"http://localhost:{target}"))
    
    # Set the cookies to expire in 30 days
    expires = datetime.now()
    expires = expires + timedelta(days=30)
    
    response.set_cookie("SUID", user_id, expires=expires, httponly=True)
    response.set_cookie("SCID", channel_id, expires=expires, httponly=True)

    return response
