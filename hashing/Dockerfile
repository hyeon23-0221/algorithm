# Python 공식 슬림 이미지 기반
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# Cloud Run 기본 포트 설정 및 Gunicorn 웹서버 구동
ENV PORT=8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
