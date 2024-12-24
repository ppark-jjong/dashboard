import requests
import pandas as pd
import time


def get_naver_coordinates(address, client_id, client_secret):
    """네이버 지도 API를 사용하여 주소의 좌표를 가져옵니다."""
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    params = {"query": address}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result.get("addresses"):
            x = float(result["addresses"][0]["x"])  # 경도
            y = float(result["addresses"][0]["y"])  # 위도
            return x, y
    return None, None


def get_route_distances(start_x, start_y, end_x, end_y, client_id, client_secret):
    """네이버 Direction5 API를 사용하여 모든 가능한 경로의 거리를 구합니다."""
    route_distances = {
        "실시간빠른길": None,
        "편한길": None,
        "최적경로": None,
        "무료우선": None,
        "자동차전용제외": None
    }

    # 모든 경로 옵션들
    options = [
        ("trafast", "실시간빠른길"),
        ("tracomfort", "편한길"),
        ("traoptimal", "최적경로"),
        ("traavoidtoll", "무료우선"),
        ("traavoidcaronly", "자동차전용제외")
    ]

    url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }

    distances = []
    for option_code, option_name in options:
        params = {
            "start": f"{start_x},{start_y}",
            "goal": f"{end_x},{end_y}",
            "option": option_code
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                result = response.json()
                if "route" in result and option_code in result["route"]:
                    distance = result["route"][option_code][0]["summary"]["distance"] / 1000
                    distance = round(distance, 2)
                    route_distances[option_name] = distance
                    distances.append((distance, option_name))
                    print(f"- {option_name}: {distance}km")

            time.sleep(0.5)  # API 호출 간격 준수

        except Exception as e:
            print(f"경로 계산 중 오류 발생 ({option_name}): {str(e)}")

    if distances:
        min_route = min(distances, key=lambda x: x[0])
        max_route = max(distances, key=lambda x: x[0])
        route_distances['최단경로'] = min_route[0]
        route_distances['최장경로'] = max_route[0]

    return route_distances


def process_addresses(csv_file, start_address, client_id, client_secret):
    """CSV 파일의 각 주소에 대해 모든 경로 거리를 계산하고 결과를 저장합니다."""
    # CSV 파일 읽기
    df = pd.read_csv(csv_file)

    # 출발지 좌표 얻기
    print(f"출발지 주소 '{start_address}' 좌표 검색 중...")
    start_x, start_y = get_naver_coordinates(start_address, client_id, client_secret)
    if not start_x or not start_y:
        raise ValueError("출발지 주소를 찾을 수 없습니다.")

    # 결과를 저장할 딕셔너리 리스트
    all_routes = []

    # 각 주소에 대해 거리 계산
    total = len(df['주소'])
    for idx, address in enumerate(df['주소'], 1):
        print(f"\n처리 중... [{idx}/{total}] : {address}")

        end_x, end_y = get_naver_coordinates(address, client_id, client_secret)
        if end_x and end_y:
            routes = get_route_distances(
                start_x, start_y, end_x, end_y,
                client_id, client_secret
            )
        else:
            print(f"⚠️ 주소를 찾을 수 없습니다: {address}")
            routes = {
                "실시간빠른길": None,
                "편한길": None,
                "최적경로": None,
                "무료우선": None,
                "자동차전용제외": None,
                "최단경로": None,
                "최단경로_타입": None,
                "최장경로": None,
                "최장경로_타입": None
            }

        all_routes.append(routes)

    # 결과를 데이터프레임에 추가
    for key in all_routes[0].keys():
        df[key] = [route[key] for route in all_routes]

    # CSV 파일로 저장
    output_file = "../data/zipcode_address_result.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 결과가 {output_file}에 저장되었습니다.")

    return df


if __name__ == "__main__":
    # 설정
    CSV_FILE = "../data/zipcode_address.csv"  # 실제 CSV 파일 경로로 변경
    START_ADDRESS = "서울 구로구 부광로 96-5"
    NAVER_CLIENT_ID = "2qxc1i2ijz"  # 네이버 클라우드 플랫폼에서 발급받은 클라이언트 ID
    NAVER_CLIENT_SECRET = "J9UWJv3QUeIPgwFNGOPMLqgcfatqh83uPTf8vXmG"  # 네이버 클라우드 플랫폼에서 발급받은 시크릿 키

    try:
        # 거리 계산 실행
        result_df = process_addresses(
            CSV_FILE,
            START_ADDRESS,
            NAVER_CLIENT_ID,
            NAVER_CLIENT_SECRET
        )
        print("\n🎉 처리가 완료되었습니다.")
        print("\n결과 미리보기:")
        print(result_df.head())

    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")