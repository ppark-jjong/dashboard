import pandas as pd
import logging
from datetime import datetime
from ..config.config_manager import ConfigManager

config = ConfigManager()

# 한글 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# 미리 정의된 컬럼 정보
COLUMNS = [
    '주문번호', 'Date(접수일)', 'DPS#', 'ETA', 'SLA', 'Ship to (1)', 'Ship to (2)',
    'Status', '1. Picked', '2. Shipped', '3. POD', 'Zip Code',
    'Billed Distance (Put into system)', '인수자'
]

# Google Sheets에서 데이터를 가져오는 공통 함수
def fetch_sheet_data():
    try:
        service = config.get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=config.SHEET_ID, range=config.RANGE_NAME).execute()
        rows = result.get('values', [])

        if not rows:
            logger.error("Google Sheets에서 데이터를 찾을 수 없습니다.")
            return None

        logger.info(f"{len(rows)}개의 데이터를 Google Sheets에서 가져왔습니다.")

        # 데이터를 DataFrame으로 변환하고, 미리 정의된 컬럼 구조를 적용
        df = pd.DataFrame(rows[1:], columns=COLUMNS)
        print("DataFrame Columns:", df.columns)  # 컬럼 구조 확인용 출력

        return df
    except Exception as e:
        logger.error(f"Google Sheets 데이터 가져오기 실패: {e}")
        return None

# ETA 기준 오늘 날짜의 데이터를 가져오는 함수
def get_today_data():
    df = fetch_sheet_data()
    if df is None:
        return None

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        df['ETA'] = pd.to_datetime(df['ETA'], errors='coerce')  # 'ETA' 컬럼을 날짜 형식으로 변환
        today_data = df[df['ETA'].dt.strftime('%Y-%m-%d') == today]  # 오늘 날짜와 일치하는 데이터 필터링
        logger.info(f"ETA가 오늘 날짜({today})인 {len(today_data)}개의 데이터를 필터링했습니다.")
        return today_data
    except KeyError as e:
        logger.error(f"컬럼을 찾을 수 없습니다: {e}")
        return None
    except Exception as e:
        logger.error(f"데이터 필터링 중 오류 발생: {e}")
        return None

# 전체 데이터를 가져오는 함수
def get_all_data():
    df = fetch_sheet_data()
    if df is None:
        return None
    return df
