from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt_util import decode_access_token

# HTTPBearer를 사용해 Authorization 헤더를 확인
http_bearer = HTTPBearer()


def require_token(credentials: HTTPAuthorizationCredentials = Security(http_bearer)):
    token = credentials.credentials
    try:
        user_payload = decode_access_token(token)
        return user_payload  # 필요한 경우 사용자 정보 반환
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
