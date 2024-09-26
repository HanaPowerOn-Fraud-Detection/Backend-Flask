from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI 
import os
import requests

app = Flask(__name__)

clova_ocr_secret = os.getenv('CLOVA_SECRET_KEY')  # Clova OCR API 비밀키
apigw_url = os.getenv('CLOVA_OCR_URL')  # Clova OCR API URL

# CORS 설정을 보다 세부적으로 정의
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST"]}})
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
MODEL="gpt-4o-mini"

@app.route('/')
def home():
    return 'Server is running!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)