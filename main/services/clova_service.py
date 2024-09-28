# clova_service.py
import requests
from flask import current_app
import uuid, time
import json
class ClovaService:
    def __init__(self):
        # CLova OCR API 관련 설정
        self.api_url = current_app.config['CLOVA_OCR_URL']
        self.secret_key = current_app.config['CLOVA_SECRET_KEY']

    def get_registration_text(self, pdf_path):
        files = [('file', open(pdf_path,'rb'))]
        request_json = {
                    'images': [{'format': 'jpeg', 'name': 'demo'}],
                    'requestId': str(uuid.uuid4()),
                    'version': 'V2',
                    'timestamp': int(round(time.time() * 1000))
                   }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}

        headers = {
        'X-OCR-SECRET': self.secret_key,
        }

        response = requests.request("POST", self.api_url, headers=headers, data=payload, files=files)
        return response.json()