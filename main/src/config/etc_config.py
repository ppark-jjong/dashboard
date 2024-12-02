import pytz
from datetime import datetime

class TimestampConfig:
    # 타임스탬프 관련 설정
    TIMEZONE = "Asia/Seoul"
    DEFAULT_FORMAT = "%y%m%d-%H%M"  # 포맷 상수화

    @staticmethod
    def get_current_timestamp():
        # 현재 타임스탬프 반환 (TIMEZONE 기준)
        return datetime.now(pytz.timezone(TimestampConfig.TIMEZONE))

    @staticmethod
    def format_timestamp(fmt=None):
        # 포맷팅된 타임스탬프 반환
        fmt = fmt or TimestampConfig.DEFAULT_FORMAT
        return TimestampConfig.get_current_timestamp().strftime(fmt)


class DashBoardConfig:
    # 대시보드 관련 설정
    DASHBOARD_COLUMNS = [
        "Delivery", "DPS", "ETA", "SLA", "Address",
        "Status", "Recipient"
    ]
