from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Secret Key is not set!")
