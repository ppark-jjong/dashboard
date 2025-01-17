from google.cloud import bigquery


def test_bigquery():
    client = bigquery.Client()
    query = """SELECT "Hello BigQuery" AS greeting"""
    result = client.query(query).result()
    for row in result:
        print(row.greeting)  # 'Hello BigQuery' 출력


if __name__ == "__main__":
    test_bigquery()
