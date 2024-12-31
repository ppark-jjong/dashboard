import requests
import pandas as pd
import time
import os


# 카카오 로컬 API (주소 -> 좌표 변환)
def get_kakao_coordinates(address, rest_api_key):
    """
    카카오 로컬 API를 사용하여 주소 -> (경도 x, 위도 y) 좌표 변환
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {rest_api_key}"
    }
    params = {
        "query": address
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        documents = result.get("documents", [])
        if len(documents) > 0:
            # x=경도, y=위도
            x = float(documents[0]["x"])
            y = float(documents[0]["y"])
            return x, y
    return None, None


# 카카오내비 API를 사용하여 (빠른길, 무료우선, 최단거리) 각각 계산 후, 최단/최장 경로를 구한다.
def get_kakao_route_distances(start_x, start_y, end_x, end_y, rest_api_key):
    """
    카카오내비 API로 3가지 옵션(빠른길=1, 무료도로=2, 최단거리=4)을 각각 요청.
    각 옵션별 distance(km)를 구한 뒤, 최단/최장 거리도 추가로 리턴한다.
    반환 예:
    {
      '빠른길': 12.3,
      '무료우선': 14.2,
      '최단거리': 10.8,
      '최단경로': 10.8,
      '최단경로_타입': '최단거리',
      '최장경로': 14.2,
      '최장경로_타입': '무료우선'
    }
    """

    # KakaoNavi API endpoint
    base_url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {
        "Authorization": f"KakaoAK {rest_api_key}"
    }

    # 이 코드에서는 "빠른길(1), 무료우선(2), 최단거리(4)" 세 가지 옵션만 사용
    option_map = {
        1: "빠른길",
        2: "무료우선",
        4: "최단거리",
    }

    route_distances = {
        "빠른길": None,
        "무료우선": None,
        "최단거리": None
    }

    for rp_option, route_name in option_map.items():
        params = {
            "origin": f"{start_x},{start_y}",
            "destination": f"{end_x},{end_y}",
            "rpOption": rp_option
        }
        try:
            resp = requests.get(base_url, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                routes = data.get("api")
                if routes and len(routes) > 0:
                    distance_m = routes[0]["summary"]["distance"]  # 미터 단위
                    distance_km = round(distance_m / 1000, 2)
                    route_distances[route_name] = distance_km
                    print(f"- {route_name}: {distance_km} km (rpOption={rp_option})")
                else:
                    print(f"결과가 없습니다. (rpOption={rp_option})")
            else:
                print(f"API 오류(rpOption={rp_option}): status={resp.status_code}, msg={resp.text}")

            time.sleep(0.3)

        except Exception as e:
            print(f"경로 계산 중 오류 발생 (rpOption={rp_option}): {str(e)}")

    # 최단/최장 경로 계산
    distances_exist = [(v, k) for k, v in route_distances.items() if v is not None]
    result_dict = {
        "빠른길": route_distances["빠른길"],
        "무료우선": route_distances["무료우선"],
        "최단거리": route_distances["최단거리"],
        "최단경로": None,
        "최단경로_타입": None,
        "최장경로": None,
        "최장경로_타입": None
    }

    if distances_exist:
        min_val, min_key = min(distances_exist, key=lambda x: x[0])
        max_val, max_key = max(distances_exist, key=lambda x: x[0])
        result_dict["최단경로"] = min_val
        result_dict["최단경로_타입"] = min_key
        result_dict["최장경로"] = max_val
        result_dict["최장경로_타입"] = max_key

    return result_dict


def process_new_rows(csv_file, start_address, kakao_rest_api_key,
                     output_file="../../data/zipcode_address_result.csv"):
    """
    - 이미 완료된 행들은 다시 계산하지 않고, 새로 들어온 행만 계산.
    - (카카오 로컬 API로 지오코딩, 카카오내비 API로 3가지 옵션 거리 계산)
    - 새 행 결과는 기존 result 파일(있다면)에 '추가(append)'.
    """

    # (1) 원본 CSV 읽기
    df_original = pd.read_csv(csv_file)
    # 'index' 컬럼이 없다면 직접 만들어줌
    if 'index' not in df_original.columns:
        print("[원본] 'index' 컬럼이 없어 새로 생성합니다.")
        df_original.insert(0, 'index', range(len(df_original)))
    # 'index'를 실제 DataFrame 인덱스로 설정
    df_original.set_index('index', inplace=True)

    print(f"원본 CSV 로드 완료! 총 행 수: {len(df_original)}")

    # (2) 결과 CSV가 이미 존재한다면 불러옴
    if os.path.exists(output_file):
        df_result = pd.read_csv(output_file)
        # 기존 result에 'index'가 없다면 만들어줌
        if 'index' not in df_result.columns:
            print("[결과] 'index' 컬럼이 없어 새로 생성합니다.")
            df_result.insert(0, 'index', range(len(df_result)))
        df_result.set_index('index', inplace=True)
        print(f"기존 결과 CSV 로드: {output_file}, shape={df_result.shape}")
    else:
        # 없다면 빈 DataFrame 준비 (컬럼만 미리 세팅)
        df_result = pd.DataFrame(columns=df_original.columns.tolist() + [
            "빠른길", "무료우선", "최단거리",
            "최단경로", "최단경로_타입", "최장경로", "최장경로_타입"
        ])
        df_result.index.name = 'index'
        print(f"결과 CSV가 없어 새로 생성 예정: {output_file}")

    # (3) 기존 결과 CSV에서 가장 큰 인덱스를 확인 => 그보다 큰 인덱스를 새로 계산
    if len(df_result) > 0:
        max_index_done = df_result.index.max()
    else:
        max_index_done = -1
    print(f"이미 완료된 행의 최대 index: {max_index_done}")

    # (4) 새로 계산해야 할 행만 필터링
    df_new = df_original[df_original.index > max_index_done]
    if len(df_new) == 0:
        print("새로 계산할 행이 없습니다. (이미 모든 행이 계산됨)")
        return df_result

    print(f"새로 계산할 행 수: {len(df_new)}")

    # (5) 출발지 좌표 얻기 (카카오 로컬 API)
    print(f"[출발지] '{start_address}' 좌표 검색 중...")
    start_x, start_y = get_kakao_coordinates(start_address, kakao_rest_api_key)
    if not start_x or not start_y:
        raise ValueError("출발지 주소(지오코딩) 실패")

    # (6) 새로 계산한 결과 담을 목록
    new_results = []
    count = 0
    for idx, row in df_new.iterrows():
        count += 1
        address = row['주소']
        print(f"\n처리 중... index={idx} [{count}/{len(df_new)}] : {address}")

        end_x, end_y = get_kakao_coordinates(address, kakao_rest_api_key)
        if end_x and end_y:
            routes = get_kakao_route_distances(start_x, start_y, end_x, end_y, kakao_rest_api_key)
        else:
            print(f"⚠️ 주소(지오코딩) 실패: {address}")
            routes = {
                "빠른길": None,
                "무료우선": None,
                "최단거리": None,
                "최단경로": None,
                "최단경로_타입": None,
                "최장경로": None,
                "최장경로_타입": None
            }

        # row + 계산결과 합치기
        data = row.to_dict()
        data.update(routes)
        data['index'] = idx  # 인덱스 번호도 넣어줌
        new_results.append(data)

    # (7) 새로 계산한 행들 => DataFrame으로 만들기
    df_new_result = pd.DataFrame(new_results)
    df_new_result.set_index('index', inplace=True)

    # (8) 기존 df_result에 수직 결합(append)
    df_result = pd.concat([df_result, df_new_result], axis=0)
    print(f"\n✅ {len(df_new_result)}건의 행을 결과에 추가했습니다. 총 결과 shape={df_result.shape}")

    # (9) 결과 CSV 저장
    df_result.to_csv(output_file, index=True, encoding='utf-8-sig')
    print(f"최종 결과가 {output_file}에 저장되었습니다.")

    return df_result


if __name__ == "__main__":
    # 설정
    CSV_FILE = "../../data/zipcode_address.csv"  # 원본 CSV
    START_ADDRESS = "서울 구로구 부광로 96-5"
    KAKAO_REST_API_KEY = "1571a59a670bbcd33efeff56407955eb"  # 카카오 디벨로퍼스에서 발급받은 REST API 키

    try:
        df_final = process_new_rows(
            csv_file=CSV_FILE,
            start_address=START_ADDRESS,
            kakao_rest_api_key=KAKAO_REST_API_KEY,
            output_file="../../data/zipcode_address_result.csv"
        )
        print("\n🎉 실행 완료!")
        print(df_final.tail(5))  # 마지막 5행만 미리보기
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
