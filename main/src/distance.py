import pandas as pd
import os


def process_address_data(file_path, output_path='processed_addresses.csv'):
    """
    텍스트 파일의 주소 데이터를 처리하고 CSV 파일로 저장하는 함수
    """
    # 텍스트 파일 읽기
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        # 헤더와 데이터 분리
        header = file.readline().strip().split('|')
        data = []
        for line in file:
            data.append(line.strip().split('|'))

    # DataFrame 생성
    df = pd.DataFrame(data, columns=header)

    try:
        # 필요한 컬럼만 선택
        address_components = df[['우편번호', '시도', '시군구', '도로명', '건물번호본번']]

        # 최종 주소 생성
        def create_full_address(row):
            # 각 구성요소 조합
            address = f"{row['시도']} {row['시군구']} {row['도로명']} {row['건물번호본번']}"
            # 불필요한 공백 제거
            address = ' '.join(address.split())
            return address

        # 새로운 데이터프레임 생성
        result_df = pd.DataFrame({
            '우편번호': address_components['우편번호'],
            '주소': address_components.apply(create_full_address, axis=1)
        })

        # CSV 파일로 저장
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f'처리된 주소가 {output_path}에 저장되었습니다.')
        return result_df

    except KeyError as e:
        print(f"오류: 필요한 컬럼을 찾을 수 없습니다. {e}")
        print("사용 가능한 컬럼:")
        print(df.columns.tolist())
        return None


# 사용 예시
if __name__ == "__main__":
    # 입력 파일 경로
    input_file = r"C:\Users\parkj\Downloads\zipcode_DB\i.txt"

    # 출력 파일 경로
    output_file = "processed_addresses_i.csv"

    # 파일이 존재하는지 확인
    if not os.path.exists(input_file):
        print(f"오류: 파일을 찾을 수 없습니다. 경로: {input_file}")
    else:
        # 함수 실행
        result = process_address_data(input_file, output_file)

        # 결과가 있을 경우에만 미리보기 출력
        if result is not None:
            print("\n처리된 데이터 미리보기:")
            print(result.head())