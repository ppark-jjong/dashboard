# data_generate.py

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random
from functools import lru_cache
import logging
from dataclasses import dataclass

@dataclass
class MetricsData:
    """배송 메트릭스 데이터 정규화 구조체"""
    total_count: int
    completion_rate: str
    in_progress: int
    pending: int

@dataclass
class RiderMetricsData:
    """기사 메트릭스 데이터 정규화 구조체"""
    active_riders: int
    avg_deliveries: str
    total_riders: int
    completion_rate: str


class DataGenerator:
    """최적화된 배송 데이터 생성 및 관리 클래스"""

    # 상수 정의
    OPERATION_TYPES = ['배송', '회수']
    DEPARTMENTS = ['물류1팀', '물류2팀', '특송팀', '신선팀']
    DELIVERY_STATUS = ['대기', '배송중', '배송완료']
    DRIVER_STATUS = ['배송중', '배송완료', '복귀중', '퇴근']
    VEHICLE_TYPES = ['1톤 화물', '2.5톤 화물', '냉장차', '오토바이']

    # 주소 샘플 데이터
    ADDRESSES = [
        "서울특별시 강남구 테헤란로 123길 45, 케이타워 8층 801호",
        "경기도 성남시 분당구 판교역로 235-2, 분당타워 15층",
        "서울특별시 송파구 올림픽로 300, 롯데월드타워 123층",
        "인천광역시 연수구 컨벤시아대로 123, 송도타워 23층"
    ]

    @staticmethod
    @lru_cache(maxsize=128)
    def generate_delivery_data(size: int = 100) -> pd.DataFrame:
        """
        배송 데이터 생성 최적화 로직
        캐시 적용으로 반복 호출 성능 향상
        """
        current_time = datetime.now()

        def generate_times() -> Dict[str, str]:
            depart = current_time + timedelta(minutes=random.randint(0, 180))
            duration = random.randint(30, 120)
            arrive = depart + timedelta(minutes=duration)
            return {
                'DepartTime': depart.strftime('%H:%M'),
                'ArriveTime': arrive.strftime('%H:%M'),
                'DeliveryDuration': f"{duration}분",
                'ETA': arrive.strftime('%Y-%m-%d %H:%M')
            }

        data = []
        for i in range(size):
            times = generate_times()
            data.append({
                'OperationType': np.random.choice(DataGenerator.OPERATION_TYPES),
                'Department': np.random.choice(DataGenerator.DEPARTMENTS),
                'Driver': f"기사{str(random.randint(1, 20)).zfill(2)}",
                'DepartTime': times['DepartTime'],
                'ArriveTime': times['ArriveTime'],
                'DeliveryDuration': times['DeliveryDuration'],
                'Status': np.random.choice(DataGenerator.DELIVERY_STATUS),
                'DPS': f"DPS{str(i + 1).zfill(6)}",
                'ETA': times['ETA'],
                'SLA': f"SLA-{random.choice(['A', 'B', 'C'])}{random.randint(1, 5)}",
                'Address': random.choice(DataGenerator.ADDRESSES),
                'Recipient': f"수령인{str(random.randint(1, 999)).zfill(3)}"
            })

        return pd.DataFrame(data)

    @staticmethod
    def generate_rider_data(size: int = 50) -> pd.DataFrame:
        """최적화된 기사 데이터 생성"""
        data = []
        for i in range(size):
            arrival_time = random.randint(15, 90)
            data.append({
                'Name': f"기사{str(i + 1).zfill(2)}",
                'Status': np.random.choice(DataGenerator.DRIVER_STATUS),
                'ArrivalTime': f"{arrival_time}분",
                'VehicleType': np.random.choice(DataGenerator.VEHICLE_TYPES),
                "Qty": random.randint(5, 30)  # Q'ty에서 Qty로 변경
            })

        return pd.DataFrame(data)


    @classmethod
    @lru_cache(maxsize=128)
    def get_delivery_metrics(cls) -> MetricsData:
        """
        배송 메트릭스 데이터 생성기
        캐시 적용으로 성능 최적화
        """
        df = cls.generate_delivery_data()
        total = len(df)
        completed = len(df[df['Status'] == '배송완료'])

        return MetricsData(
            total_count=total,
            completion_rate=f"{(completed / total * 100):.1f}%",
            in_progress=len(df[df['Status'] == '배송중']),
            pending=len(df[df['Status'] == '대기'])
        )

    @classmethod
    def get_rider_metrics(cls) -> Dict[str, Any]:
        """기사 메트릭스 생성기 v2.0"""
        df = cls.generate_rider_data()
        total = len(df)
        active = len(df[df['Status'].isin(['배송중', '복귀중'])])

        return {
            'active_riders': active,
            'total_riders': total,
            'avg_deliveries': f"{df['Qty'].mean():.1f}건",
            'completion_rate': f"{(len(df[df['Status'] == '배송완료']) / total * 100):.1f}%"
        }

    @classmethod
    def get_column_definitions(cls) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
        """컬럼 정의 메타데이터 관리자"""
        return {
            'delivery': {
                'columns': [
                    {'name': '작업유형', 'id': 'OperationType'},
                    {'name': '담당부서', 'id': 'Department'},
                    {'name': '기사명', 'id': 'Driver'},
                    {'name': '출발시간', 'id': 'DepartTime'},
                    {'name': '도착예정', 'id': 'ArriveTime'},
                    {'name': '소요시간', 'id': 'DeliveryDuration'},
                    {'name': '상태', 'id': 'Status'},
                    {'name': 'DPS번호', 'id': 'DPS'},
                    {'name': '완료예정', 'id': 'ETA'},
                    {'name': 'SLA등급', 'id': 'SLA'},
                    {'name': '배송주소', 'id': 'Address'},
                    {'name': '수령인', 'id': 'Recipient'}
                ]
            },
            'rider': {
                'columns': [
                    {'name': '기사명', 'id': 'Name'},
                    {'name': '상태', 'id': 'Status'},
                    {'name': '도착예정', 'id': 'ArrivalTime'},
                    {'name': '차량유형', 'id': 'VehicleType'},
                    {'name': '배송건수', 'id': 'Qty'}
                ]
            }
        }
