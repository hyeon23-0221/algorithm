# ==========================================
# Google Cloud Run 배포용 경량 Python 컨테이너
# ==========================================
FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 (Cloud Run 로깅 최적화)
ENV PYTHONUNBUFFERED=1

# Cloud Run 기본 포트 환경변수 설정
ENV PORT=8080

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치 (캐시 레이어 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 포트 노출 선언
EXPOSE 8080

# Cloud Run 시작 명령어 (PORT 환경 변수를 동적으로 수신)
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}

