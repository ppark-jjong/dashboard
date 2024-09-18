import pandas as pd

# 데이터 파일을 로드하여 DataFrame으로 반환
def load_data(file_path):
    print("데이터를 로드하고 있습니다...")
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    print("데이터 로드 완료.")
    return data

# 데이터 전처리 함수
def preprocess_data(data):
    print("데이터 전처리를 진행 중입니다...")
    data['Date(접수일)'] = pd.to_datetime(data['Date(접수일)'])
    data['Week'] = data['Date(접수일)'].dt.to_period('W')
    data['Weekday'] = data['Date(접수일)'].dt.day_name()
    data['Completed'] = data['Status'] == 'Completed'
    print("데이터 전처리 완료.")
    return data

# 일별 분석 함수
def daily_analysis(data, date):
    print(f"{date}의 일별 데이터를 분석합니다...")
    daily_data = data[data['Date(접수일)'].dt.date == date]
    status_counts = daily_data['Status'].value_counts()
    completion_rate = daily_data['Completed'].mean() * 100
    avg_distance = daily_data['Billed Distance (Put into system)'].mean()
    issue_count = daily_data['issue'].eq('O').sum()
    print("일별 분석 완료.")
    return status_counts, completion_rate, avg_distance, issue_count

# 주별 분석 함수
def weekly_analysis(data, week):
    print(f"{week}의 주별 데이터를 분석합니다...")
    weekly_data = data[data['Week'] == week]
    completion_rate = weekly_data['Completed'].mean() * 100
    avg_distance = weekly_data['Billed Distance (Put into system)'].mean()
    issue_count = weekly_data['issue'].eq('O').sum()
    print("주별 분석 완료.")
    return completion_rate, avg_distance, issue_count

# 이슈 패턴 분석 함수
def analyze_issue_pattern(data):
    print("이슈 발생 패턴을 분석합니다...")
    issue_pattern = data[data['issue'] == 'O'].groupby('Weekday')['DPS#'].count().sort_index()
    print("이슈 패턴 분석 완료.")
    return issue_pattern
