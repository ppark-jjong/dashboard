import logging
from logging.handlers import RotatingFileHandler
import os


class Logger:
    # 로깅 설정 관리

    @staticmethod
    def get_logger(name: str = __name__, log_file: str = None, level: int = logging.INFO):
        # 로거 객체 반환
        logger = logging.getLogger(name)

        if not logger.handlers:
            logger.setLevel(level)

            # 핸들러 설정
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            log_file = log_file or os.getenv("LOG_FILE", "./logs/default.log")  # 기본 경로 환경변수화
            file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            # 핸들러 추가
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger
