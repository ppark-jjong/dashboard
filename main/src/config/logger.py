import logging
from logging.handlers import RotatingFileHandler


class Logger:

    @staticmethod
    def get_logger(name: str = __name__, log_file: str = None):
        logger = logging.getLogger(name)

        # 중복 핸들러 방지
        if not logger.handlers:
            # 기본 로깅 설정
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # 콘솔 핸들러 추가
            console_handler = logging.StreamHandler()
            logger.addHandler(console_handler)

            # 파일 핸들러 추가
            if log_file:
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=5 * 1024 * 1024, backupCount=2
                )
                file_handler.setFormatter(
                    logging.Formatter(
                        '%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                    )
                )
                logger.addHandler(file_handler)

        return logger
