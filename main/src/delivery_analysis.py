import pandas as pd

# 데이터 파일을 로드하여 DataFrame으로 반환
def load_data(file_path):
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    return data

# 데이터 전처리
def preprocess_data(data):
    data['Date(접수일)'] = pd.to_datetime(data['Date(접수일)'])
    data['Week'] = data['Date(접수일)'].dt.to_period('W')
    data['Weekday'] = data['Date(접수일)'].dt.day_name()
    data['Completed'] = data['Status'] == 'Completed'
    return data

# 일별 거리, 완료율, 이슈 분석
def daily_analysis(data, date):
    daily_data = data[data['Date(접수일)'].dt.date == date]

    status_counts = daily_data['Status'].value_counts()
    completion_rate = daily_data['Completed'].mean() * 100
    avg_distance = daily_data['Billed Distance (Put into system)'].mean()
    issue_count = daily_data['issue'].eq('O').sum()

    return status_counts, completion_rate, avg_distance, issue_count

# 주별 거리, 완료율, 이슈 분석
def weekly_analysis(data, week):
    weekly_data = data[data['Week'] == week]

    completion_rate = weekly_data['Completed'].mean() * 100
    avg_distance = weekly_data['Billed Distance (Put into system)'].mean()
    issue_count = weekly_data['issue'].eq('O').sum()

    return completion_rate, avg_distance, issue_count

# 이슈 발생 패턴 분석
def analyze_issue_pattern(data):
    issue_pattern = data[data['issue'] == 'O'].groupby('Weekday')['DPS#'].count().sort_index()
    return issue_pattern