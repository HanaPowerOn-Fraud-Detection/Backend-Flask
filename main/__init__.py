# __init__.py

# fraud_detection 모듈 초기화

# 필요한 서브 모듈을 임포트
from .services import gpt_service  # GPT 서비스 모듈 임포트
from .services import clova_service  # CLova OCR 서비스 모듈 임포트
from .apis import api_bp  # API 모듈 임포트
from .models import db

__all__ = [
    'gpt_service',  # GPT API 서비스의 공개 객체
    'clova_service',  # CLova OCR API 서비스의 공개 객체
    'api_bp',  # APIs 모듈의 API 객체
]

# 모듈 초기화와 관련된 추가 설정이나 함수 정의
def initialize():
    print("Fraud Detection 서비스가 초기화되었습니다.")
