from flask import Flask, request, Response
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5175', 'http://localhost:5173'], supports_credentials=True)

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()  # Or return Response('', status=200)

from functions.check import check
from functions.oauth_handler.app_auth import verify_cookie, set_cookies, web_app_auth
from functions.studio_handler.upload import upload_file  
from functions.client_handler.get_playing_video import get_playing_video
from functions.client_handler.get_recommended_videos import get_recommended_videos


app.route('/check', methods=['GET', "OPTIONS"])(check)

# oauth
app.route('/Verify-cookie', methods=['GET', "OPTIONS"])(verify_cookie)

app.route('/Set-cookie', methods=['GET', "OPTIONS"])(set_cookies)

app.route('/Web-App-Auth', methods=['GET', "OPTIONS"])(web_app_auth)
# oauth

# studio
app.route('/upload', methods=['POST', 'GET', 'OPTIONS'])(upload_file)
# studio

# client
app.route('/browse', methods=['POST', 'GET', 'OPTIONS'])(get_recommended_videos)
app.route('/watch-video', methods=['POST', 'GET', 'OPTIONS'])(get_playing_video)
# client


serve(app, host='0.0.0.0', port=8220)
