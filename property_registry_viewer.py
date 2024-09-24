import requests
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수를 불러옴
load_dotenv()

# 인증키 가져오기
auth_key = os.getenv('APICK_CLIENT_API_KEY')
# 주소 및 부동산 고유번호 설정
unique_num = '2601-2022-018207'

# API 요청 URL
url = 'https://apick.app/rest/iros/1'

# POST 요청
response = requests.post(url, headers={"CL_AUTH_KEY": auth_key}, data={"unique_num" : unique_num})

print(response.request.body)

# 결과 출력
if response.status_code == 200:
    print("Response:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")