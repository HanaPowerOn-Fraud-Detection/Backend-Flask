# clova_service.py
import requests

class ClovaService:
    def __init__(self):
        # CLova OCR API 관련 설정
        self.api_url = "https://clova.ai/ocr"
        self.api_key = "your_clova_api_key"

    def call_clova_ocr(self, image_data):
        headers = {
            "X-OCR-SECRET": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "images": [{"format": "jpg", "data": image_data}],
            "requestId": "ocr_request",
            "version": "V2"
        }

        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "CLova OCR API 호출 실패", "status_code": response.status_code}
