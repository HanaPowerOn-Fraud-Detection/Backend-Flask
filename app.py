from flask import Flask
from flask_cors import CORS
from main import api_bp
from config import Config
from error_handlers import register_error_handlers 
import os

# Flask 애플리케이션 생성
app = Flask(__name__, instance_relative_config=True)

# CORS 설정
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST"]}})

# 설정 파일 로드
app.config.from_object(Config)

# 블루프린트 등록 (API와 라우트 경로를 등록)
app.register_blueprint(api_bp, url_prefix='/api')  # '/api' 경로에 모든 API 등록


# 예외 처리 핸들러 등록
register_error_handlers(app)


if __name__ == '__main__':
    # 환경 변수에서 포트 가져오기, 기본 포트는 5000으로 설정
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
