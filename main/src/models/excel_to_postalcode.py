import pandas as pd
import mysql.connector

# 엑셀 파일 경로
file_path = "../../data/postal_code.xlsx"

# 엑셀 데이터 읽기
df = pd.read_excel(file_path)
# 데이터 타입 변환
df['postal_code'] = df['postal_code'].astype(str)  # postal_code를 문자열로 변환
df['duration_time'] = df['duration_time'].fillna(0).astype(int)  # Null 값을 0으로 대체 후 정수로 변환
df['distance'] = df['distance'].fillna(0).astype(int)  # Null 값을 0으로 대체 후 정수로 변환
# MySQL 연결 정보
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'delivery_system'
}

# 데이터베이스 연결
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 데이터 삽입
    insert_query = """
        INSERT INTO postal_code (postal_code, duration_time, distance)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            duration_time = VALUES(duration_time),
            distance = VALUES(distance)
    """

    # 데이터프레임의 각 행을 삽입
    for _, row in df.iterrows():
        cursor.execute(insert_query, (row['postal_code'], row['duration_time'], row['distance']))

    connection.commit()
    print("데이터 삽입 완료!")

except mysql.connector.Error as err:
    print(f"에러: {err}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL 연결이 종료되었습니다.")
