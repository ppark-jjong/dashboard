import os
import logging
from logging.handlers import RotatingFileHandler

class Logger:
    @staticmethod
    def get_logger(name, log_file="logs/default.log"):
        # 로그 디렉토리 확인 및 생성
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 로거 설정
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # 로그 파일 핸들러 추가
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 중복 핸들러 추가 방지
        if not logger.handlers:
            logger.addHandler(file_handler)

        return logger
