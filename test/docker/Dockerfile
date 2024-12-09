# Python 기반 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt requirements.txt

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 앱 실행
CMD ["python", "main.py"]
