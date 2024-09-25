# 베이스 이미지 설정
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# Flask 애플리케이션 종속성 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .
COPY .env .env

# 포트 노출
EXPOSE 5000

# Flask 애플리케이션 실행
CMD ["python", "server.py"]
