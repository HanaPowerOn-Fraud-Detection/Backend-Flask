# clova_service.py
import requests
from flask import current_app
import uuid, time
import json
class ClovaService:
    def __init__(self):
        # CLova OCR API 관련 설정
        self.api_url = current_app.config['CLOVA_OCR_URL']
        self.api_key = current_app.config['CLOVA_SECRET_KEY']

    def get_registration_text(self, image_paths):
        headers = {
            "X-OCR-SECRET": self.api_key
        }

        request_json = {
            'images': [{'format': 'jpeg', 'name': 'demo'} for _ in image_paths],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        files = [('file', open(img, 'rb')) for img in image_paths]

        response = requests.post(self.api_url, headers=headers, data={'message': json.dumps(request_json).encode('UTF-8')}, files=files)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "CLova OCR API 호출 실패", "status_code": response.status_code}
