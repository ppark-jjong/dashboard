from src.collectors.google_sheets_collector import get_today_data, get_all_data
from kafka.producer import create_kafka_producer, send_to_kafka

# def main():
#     producer = create_kafka_producer()
#
#     # 오늘의 데이터 가져와 Kafka로 전송
#     today_data = get_today_data()
#     send_to_kafka(producer, 'today_delivery_data', today_data)
#
#     # 전체 데이터 가져와 Kafka로 전송
#     all_data = get_all_data()
#     send_to_kafka(producer, 'all_delivery_data', all_data)
#
# if __name__ == "__main__":
#     main()
