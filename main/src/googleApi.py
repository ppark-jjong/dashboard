import pandas as pd
from datetime import datetime
from googleapiclient.errors import HttpError
from proto import dashboard_status_pb2
from proto import monthly_volume_status_pb2
<<<<<<< HEAD
=======
from config_manager import ConfigManager

config = ConfigManager()
>>>>>>> origin/main

def get_sheet_data():
    try:
        print(f"[정보] Google Sheets API에 접근 중...")
        service = config.get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=config.SHEET_ID, range=config.RANGE_NAME).execute()
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
        picked_count=int(status_counts['1. Picked']),
        shipped_count=int(status_counts['2. Shipped']),
        pod_count=int(status_counts['3. POD']),
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
        distance_counts={int(k): v for k, v in distance_counts.items()}
    )

    print("[성공] 데이터 전처리 및 직렬화 완료")
    return dashboard_status, monthly_volume_status