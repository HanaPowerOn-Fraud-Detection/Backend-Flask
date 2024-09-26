# gpt_service.py
import requests

class GPTService:
    def __init__(self):
        # API 키나 엔드포인트와 같은 GPT API 관련 설정
        self.api_url = "https://api.openai.com/v1/completions"
        self.api_key = "your_openai_api_key"

    def call_gpt(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "prompt": prompt,
            "max_tokens": 100
        }

        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "GPT API 호출 실패", "status_code": response.status_code}
