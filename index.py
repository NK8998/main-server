import asyncio
from flask import Flask, request, Response
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv
from server_globals.secrets import get_secret
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5175', 'http://localhost:5173', 'http://localhost:5174', 'https://client-red-nine.vercel.app/', 'https://studio-chi-one.vercel.app/', 'https://o-auth-alpha.vercel.app/'], supports_credentials=True)

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()  # Or return Response('', status=200)

from endpoints.check import check
from endpoints.oauth_handler.app_auth import verify_cookie, set_cookies, web_app_auth, verify_credentials

from endpoints.studio_handler.upload import upload_file  
from endpoints.studio_handler.additional_video_data import additional_video_data
from endpoints.studio_handler.get_users_videos import get_users_videos
from endpoints.studio_handler.delete_video import initiate_video_deletion

from endpoints.client_handler.get_playing_video import get_playing_video
from endpoints.client_handler.get_recommended_videos import get_recommended_videos
from endpoints.client_handler.comments.post_comment import post_comment
from endpoints.client_handler.comments.get_comments import get_comments

from server_globals.SDKs import get_boto3_client


app.route('/check', methods=['GET', "OPTIONS"])(check)

# oauth
app.route('/Verify-cookie', methods=['GET', "OPTIONS"])(verify_cookie)
app.route('/Set-cookie', methods=['GET', "OPTIONS"])(set_cookies)
app.route('/Web-App-Auth', methods=['GET', "OPTIONS"])(web_app_auth)
# oauth

# studio
app.route('/upload', methods=['POST', 'GET', 'OPTIONS'])(upload_file)
app.route('/additional-video-data', methods=['POST', 'GET', 'OPTIONS'])(additional_video_data)
app.route('/get-users-videos', methods=['POST', 'GET', 'OPTIONS'])(get_users_videos)
app.route('/delete-video', methods=['POST', 'GET', 'OPTIONS'])(initiate_video_deletion)
# studio

# client
app.route('/verify-credentials', methods=['POST', 'GET', 'OPTIONS'])(verify_credentials)
app.route('/browse', methods=['POST', 'GET', 'OPTIONS'])(get_recommended_videos)
app.route('/watch-video', methods=['POST', 'GET', 'OPTIONS'])(get_playing_video)
app.route('/post-comment', methods=['POST', 'GET', 'OPTIONS'])(post_comment)
app.route('/get-comments', methods=['POST', 'GET', 'OPTIONS'])(get_comments)
# client


async def init():
    await get_secret('hive_credentials')
# Run the async function before starting the server
asyncio.run(init())

serve(app, host='0.0.0.0', port=8220)