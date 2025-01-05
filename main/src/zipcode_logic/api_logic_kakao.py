with open("C:/MyMain/dashboard/main/data/zipcode_address_result.csv", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

with open("C:/MyMain/dashboard/main/data/zipcode_address_result_utf.csv", "w", encoding="utf-8") as f:
    f.write(content)

print("파일이 UTF-8로 변환되었습니다.")
