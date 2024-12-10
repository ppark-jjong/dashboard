import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_delivery_data(num_records=100):
    """
    Generate a comprehensive sample delivery dataset

    Args:
        num_records (int): Number of delivery records to generate

    Returns:
        pandas.DataFrame: Simulated delivery data
    """
    # Delivery Types
    delivery_types = ['방문수령', '대리수령', '무인함', '직접전달', '보관함']

    # Departments
    departments = ['Logistics', 'Express', 'Special Delivery', 'Urban Delivery', 'Rural Delivery']

    # Delivery Statuses
    statuses = ['배송대기', '배송중', '배송완료', '문제발생']

    # Receivers
    first_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
    last_names = ['철수', '영희', '민수', '지영', '현우', '서연', '태영', '미란', '준호', '은주']

    # Cities and Addresses
    cities = ['서울', '부산', '인천', '대구', '광주', '대전', '울산']
    streets = ['Street', 'Road', 'Avenue', 'Lane', 'Boulevard']

    # Generate data
    data = []
    for i in range(num_records):
        # Random data generation
        delivery_date = datetime.now() + timedelta(days=np.random.randint(0, 5))
        departure_time = delivery_date.replace(hour=np.random.randint(6, 18), minute=np.random.randint(0, 59))
        eta = departure_time + timedelta(hours=np.random.randint(1, 6))

        record = {
            'DPS': f'DPS{np.random.randint(1000, 9999)}',
            '배송종류': np.random.choice(delivery_types),
            '담당부서': np.random.choice(departments),
            '상태': np.random.choice(statuses),
            '출발시간': departure_time.strftime('%H:%M'),
            'ETA': eta.strftime('%Y-%m-%d %H:%M'),
            '주소': f'{np.random.choice(cities)} {np.random.randint(1, 100)} {np.random.choice(streets)}',
            '수령인': f'{np.random.choice(first_names)}{np.random.choice(last_names)}',
            '연락처': f'010-{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}',
            '무게': round(np.random.uniform(0.1, 50.0), 2),  # kg
            '크기': np.random.choice(['소형', '중형', '대형']),
            '배송비': round(np.random.uniform(1000, 20000), 2),  # KRW
            '할인율': round(np.random.uniform(0, 30), 2)  # Percentage
        }
        data.append(record)

    # Create DataFrame and insert sequential number
    df = pd.DataFrame(data)
    df.insert(0, 'No.', range(1, len(df) + 1))

    return df


# # Example usage and data preview
# if __name__ == "__main__":
#     delivery_data = generate_sample_delivery_data(10)
#     print(delivery_data)
#
#     # Optional: Save to CSV for further analysis
#     delivery_data.to_csv('sample_delivery_data.csv', index=False, encoding='utf-8-sig')