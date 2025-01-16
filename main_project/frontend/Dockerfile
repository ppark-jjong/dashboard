# /frontend/DockerFile


# 프로덕션용 Nginx 설정
FROM nginx:alpine

# Nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 정적 파일 복사
COPY . /usr/share/nginx/html

EXPOSE 80