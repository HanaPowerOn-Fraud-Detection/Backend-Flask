# fraud_detection/apis/__init__.py

from .api import api_bp  # api.py에서 api_bp를 임포트

__all__ = ['api_bp']  # api_bp를 공개 객체로 설정
