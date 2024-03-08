from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:5175', 'http://localhost:5173'], supports_credentials=True)

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()  # Or return Response('', status=200)

from functions.app_auth import verify_cookie, set_cookies, web_app_auth
from functions.upload import upload_file  # import the function from upload.py
from functions.check import check
from dotenv import load_dotenv

load_dotenv()


app.route('/Verify-cookie', methods=['GET', "OPTIONS"])(verify_cookie)

app.route('/Set-cookie', methods=['GET', "OPTIONS"])(set_cookies)

app.route('/Web-App-Auth', methods=['GET', "OPTIONS"])(web_app_auth)

app.route('/upload', methods=['POST', 'GET', 'OPTIONS'])(upload_file)

app.route('/check', methods=['GET', "OPTIONS"])(check)


if __name__ == '__main__':
    app.run(debug=True)
