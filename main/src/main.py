from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path
from models.db_model import Base, Driver, Dashboard, Delivery, Return, PostalCode


def create_connection_uri() -> str:
    """환경 변수에서 데이터베이스 연결 URI 생성"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key.strip()] = value.strip()

    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')

    return f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/delivery_system'


def compare_table_structures():
    """데이터베이스의 실제 테이블 구조와 모델 구조 비교"""
    print("\n=== Database Structure Check ===")

    try:
        engine = create_engine(create_connection_uri())
        inspector = inspect(engine)

        with engine.connect() as connection:
            # 실제 데이터베이스의 테이블 구조 조회
            print("\nCurrent Database Structure:")
            existing_tables = inspector.get_table_names()

            # Model에 정의된 테이블 목록
            model_tables = Base.metadata.tables.keys()

            print("\nTable Comparison:")
            print(f"Model defined tables: {sorted(list(model_tables))}")
            print(f"Existing database tables: {sorted(existing_tables)}")

            # 각 테이블별 상세 비교
            print("\nDetailed Structure Comparison:")
            for table_name in existing_tables:
                print(f"\nTable: {table_name}")

                # 실제 DB 컬럼 정보
                columns = inspector.get_columns(table_name)
                print("Database Columns:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"    {nullable}")
                    if col.get('default') is not None:
                        print(f"    Default: {col['default']}")

                # 외래 키 정보
                fk_query = text("""
                    SELECT 
                        COLUMN_NAME,
                        REFERENCED_TABLE_NAME,
                        REFERENCED_COLUMN_NAME
                    FROM
                        information_schema.KEY_COLUMN_USAGE
                    WHERE
                        TABLE_SCHEMA = 'delivery_system'
                        AND TABLE_NAME = :table_name
                        AND REFERENCED_TABLE_NAME IS NOT NULL
                """)
                fk_result = connection.execute(fk_query, {"table_name": table_name})
                fks = fk_result.fetchall()
                if fks:
                    print("  Foreign Keys:")
                    for fk in fks:
                        print(f"    - {fk[0]} -> {fk[1]}({fk[2]})")

                # 인덱스 정보
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    print("  Indexes:")
                    for idx in indexes:
                        print(f"    - {idx['name']}: columns={idx['column_names']}, unique={idx['unique']}")

        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    # .env 파일 로드
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path, override=True)
    compare_table_structures()