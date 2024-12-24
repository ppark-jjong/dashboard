import requests
import pandas as pd
import time
import csv


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


def get_driving_distance_direction5(start_x, start_y, end_x, end_y, client_id, client_secret):
    """네이버 Direction5 API를 사용하여 운전 경로 거리를 계산합니다."""
    url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    params = {
        "start": f"{start_x},{start_y}",
        "goal": f"{end_x},{end_y}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
            if "route" in result and "traoptimal" in result["route"]:
                distance_km = round(result["route"]["traoptimal"][0]["summary"]["distance"] / 1000, 2)
                return distance_km
    except Exception as e:
        print(f"경로 계산 중 오류 발생: {str(e)}")

    return None


def calculate_distances(csv_file, start_address, client_id, client_secret):
    """CSV 파일의 주소들에 대해 거리를 계산하고 결과를 추가합니다."""
    # CSV 파일 읽기
    df = pd.read_csv(csv_file)

    # 출발지 좌표 얻기
    print(f"출발지 주소 '{start_address}' 좌표 검색 중...")
    start_x, start_y = get_naver_coordinates(start_address, client_id, client_secret)
    if not start_x or not start_y:
        raise ValueError("출발지 주소를 찾을 수 없습니다.")

    # 결과를 저장할 리스트
    distances = []

    # 각 주소에 대해 거리 계산
    total = len(df['주소'])
    for idx, address in enumerate(df['주소'], 1):
        print(f"처리 중... [{idx}/{total}] : {address}")

        end_x, end_y = get_naver_coordinates(address, client_id, client_secret)
        if end_x and end_y:
            distance = get_driving_distance_direction5(
                start_x, start_y, end_x, end_y,
                client_id, client_secret
            )
            distances.append(distance)
        else:
            print(f"  ⚠️ 주소를 찾을 수 없습니다: {address}")
            distances.append(None)

        # API 호출 제한을 위한 딜레이
        time.sleep(0.5)

    # 거리가 None이 아닌 값들만 필터링하여 최단/최장 거리 계산
    valid_distances = [d for d in distances if d is not None]
    min_distance = min(valid_distances) if valid_distances else None
    max_distance = max(valid_distances) if valid_distances else None

    # 결과를 데이터프레임에 추가
    df['도로거리(km)'] = distances
    df['최단거리(km)'] = min_distance
    df['최장거리(km)'] = max_distance

    # CSV 파일로 저장
    output_file = f"processed_{csv_file}"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 결과가 {output_file}에 저장되었습니다.")
    print(f"최단거리: {min_distance}km")
    print(f"최장거리: {max_distance}km")

    return df


if __name__ == "__main__":
    # 설정
    CSV_FILE = "processed_addresses_b.csv"  # 실제 CSV 파일 경로로 변경
    START_ADDRESS = "서울 구로구 부광로 96-5"
    NAVER_CLIENT_ID = "2qxc1i2ijz"  # 네이버 클라우드 플랫폼에서 발급받은 클라이언트 ID
    NAVER_CLIENT_SECRET = "J9UWJv3QUeIPgwFNGOPMLqgcfatqh83uPTf8vXmG"  # 네이버 클라우드 플랫폼에서 발급받은 시크릿 키

    try:
        # 거리 계산 실행
        result_df = calculate_distances(
            CSV_FILE,
            START_ADDRESS,
            NAVER_CLIENT_ID,
            NAVER_CLIENT_SECRET
        )
        print("\n🎉 처리가 완료되었습니다.")

    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")