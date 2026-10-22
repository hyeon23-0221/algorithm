# Python 공식 슬림 이미지 사용
FROM python:3.11-slim

# 작업 디렉터리 설정
WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Cloud Run 호환을 위한 Port 설정 및 Gunicorn 웹서버 실행
ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
