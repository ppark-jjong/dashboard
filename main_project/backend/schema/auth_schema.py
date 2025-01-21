from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_id: str
    password: str


class LoginResponse(BaseModel):
    session_token: str
    message: str
