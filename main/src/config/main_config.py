import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')

    # MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'MYSQL',
        'mysql+mysqlconnector://teckwahkr-db:1234@mysql:3306/delivery_system'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')