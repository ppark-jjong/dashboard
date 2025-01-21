from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


# JWT 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# JWT 검증
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# HTTPBearer로 Authorization 헤더 검증
http_bearer = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(http_bearer)):
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload  # 필요하면 사용자 데이터 반환
