import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # 기본 비밀키
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # 데이터베이스 URL

    # API 관련 환경 변수
    APICK_CLIENT_API_KEY = os.getenv('APICK_CLIENT_API_KEY')
    IC_ID = os.getenv('IC_ID')
    CLOVA_SECRET_KEY = os.getenv('CLOVA_SECRET_KEY')
    CLOVA_OCR_URL = os.getenv('CLOVA_OCR_URL')
    GPT_SECRET_KEY = os.getenv('GPT_SECRET_KEY')
