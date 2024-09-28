import os
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from protos import dashboard_status_pb2
from protos import monthly_volume_status_pb2

# Google Sheets API 설정
SHEET_ID = os.environ.get('SHEET_ID', '1x4P2VO-ZArT7ibSYywFIBXUTapBhUnE4_ouVMKrKBwc')
RANGE_NAME = os.environ.get('RANGE_NAME', 'Sheet1!A1:o1000')
SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE', 'C:/MyMain/oauth/google/credentials.json')
def get_sheet_data():
    try:
        print(f"[정보] Google Sheets API에 접근 중...")
        print(f"[정보] SHEET_ID: {SHEET_ID}")
        print(f"[정보] RANGE_NAME: {RANGE_NAME}")
        print(f"[정보] SERVICE_ACCOUNT_FILE: {SERVICE_ACCOUNT_FILE}")

        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"[오류] Service account file이 존재하지 않습니다: {SERVICE_ACCOUNT_FILE}")
            return None

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        service = build('sheets', 'v4', credentials=credentials)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        rows = result.get('values', [])

        if not rows:
            print("[오류] 데이터가 없습니다.")
            return None

        print("[성공] Google Sheets에서 데이터 가져오기 완료")
        data = rows[1:]
        return data

    except HttpError as err:
        print(f"[오류] Google Sheets 데이터를 불러오는 중 오류 발생: {err}")
        return None
    except Exception as e:
        print(f"[오류] 예기치 않은 오류 발생: {e}")
        return None
def preprocess_data(data):
    print("[정보] 데이터 전처리 중...")

    df = pd.DataFrame(data, columns=[
        '배송 기사', 'Date(접수일)', 'DPS#', 'ETA', 'SLA', 'Ship to', 'Status',
        '1. Picked', '2. Shipped', '3. POD', 'Zip Code', 'Billed Distance (Put into system)', '인수자', 'issue'
    ])

    today = datetime.now().strftime('%Y-%m-%d')
    today_data = df[df['Date(접수일)'] == today]

    # 실시간 대시보드 용 데이터 = dashboard_status
    status_counts = today_data[['1. Picked', '2. Shipped', '3. POD']].apply(lambda x: x == 'O').sum()
    sla_counts_today = today_data.groupby('SLA').size().to_dict()
    issues_today = today_data[today_data['issue'] == 'O']['DPS#'].tolist()

    dashboard_status = dashboard_status_pb2.DashboardStatus(
        picked_count=status_counts['1. Picked'],
        shipped_count=status_counts['2. Shipped'],
        pod_count=status_counts['3. POD'],
        sla_counts_today=sla_counts_today,
        issues_today=issues_today
    )

    # 매달 배송 현황 볼륨 용 데이터 = monthly_volume_status
    sla_counts_month = df.groupby('SLA').size().to_dict()
    df['요일'] = pd.to_datetime(df['Date(접수일)']).dt.day_name()
    weekday_counts = df.groupby('요일').size().to_dict()
    df['거리 범위'] = (df['Billed Distance (Put into system)'].astype(int) // 20) * 20
    distance_counts = df.groupby('거리 범위').size().to_dict()

    monthly_volume_status = monthly_volume_status_pb2.MonthlyVolumeStatus(
        sla_counts_month=sla_counts_month,
        weekday_counts=weekday_counts,
        distance_counts=distance_counts
    )

    print("[성공] 데이터 전처리 및 직렬화 완료")
    return dashboard_status, monthly_volume_status
