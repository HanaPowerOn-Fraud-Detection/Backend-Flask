import requests
import hashlib
from dotenv import load_dotenv
import os


# .env 파일에서 환경 변수를 불러옴
load_dotenv()

# 인증키 가져오기
auth_key = os.getenv('APICK_CLIENT_API_KEY')
ic_id = os.getenv('IC_ID')


# API 요청 URL
r = requests.post("https://apick.app/rest/iros_download/1", headers={"CL_AUTH_KEY": auth_key}, data={"ic_id" : int(3133699)})
print("ic_id 출력값 : ", ic_id)
print("request body 출력값 : ", r.request.body)
if r.status_code == 200:
    # PDF 형식의 바이너리 데이터를 변수에 저장
    pdf_data = r.content  # 바이너리 데이터
    pdf_path = 'result.pdf'
    
    # PDF 데이터를 파일로 저장
    with open(pdf_path, "wb") as f:
        f.write(r.content)
    print(f"PDF saved at {pdf_path}")
else:
    print(f"Error: {r.status_code}, {r.text}")


