from .redis_service import get_delivery_data, get_driver_data

def fetch_data():
    # Redis에서 데이터를 가져오는 로직
    delivery_data = get_delivery_data()
    driver_data = get_driver_data()
    return delivery_data, driver_data
