from flask import Flask, request, Response
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5175', 'http://localhost:5173', 'http://localhost:5174'], supports_credentials=True)

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()  # Or return Response('', status=200)

from endpoints.check import check
from endpoints.oauth_handler.app_auth import verify_cookie, set_cookies, web_app_auth, verify_credentials
from endpoints.studio_handler.upload import upload_file  
from endpoints.studio_handler.additional_video_data import additional_video_data
from endpoints.client_handler.get_playing_video import get_playing_video
from endpoints.client_handler.get_recommended_videos import get_recommended_videos


app.route('/check', methods=['GET', "OPTIONS"])(check)

# oauth
app.route('/Verify-cookie', methods=['GET', "OPTIONS"])(verify_cookie)

app.route('/Set-cookie', methods=['GET', "OPTIONS"])(set_cookies)

app.route('/Web-App-Auth', methods=['GET', "OPTIONS"])(web_app_auth)
# oauth

# studio
app.route('/upload', methods=['POST', 'GET', 'OPTIONS'])(upload_file)
app.route('/additional-video-data', methods=['POST', 'GET', 'OPTIONS'])(additional_video_data)
# studio

# client
app.route('/verify-credentials', methods=['POST', 'GET', 'OPTIONS'])(verify_credentials)
app.route('/browse', methods=['POST', 'GET', 'OPTIONS'])(get_recommended_videos)
app.route('/watch-video', methods=['POST', 'GET', 'OPTIONS'])(get_playing_video)
# client


serve(app, host='0.0.0.0', port=8220)
