-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS delivery_system;

-- 데이터베이스 선택
USE delivery_system;

-- 배송 테이블 생성
CREATE TABLE delivery (
    dps VARCHAR(50) PRIMARY KEY,
    eta TIMESTAMP NOT NULL,
    sla VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    recipient VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    remark TEXT,
    depart_time TIMESTAMP NULL,
    arrive_time TIMESTAMP NULL,
    delivery_duration INTEGER NULL,
    department VARCHAR(100) NULL,
    delivery VARCHAR(100) NULL,
    reason TEXT NULL,
    status INTEGER NULL CHECK (status IN (0, 1, 2, 3)) -- 0: 대기, 1: 배송, 2: 완료, 3: 이슈
);

-- 회수 테이블 생성 (독립적인 테이블)
CREATE TABLE return_delivery (
    dps VARCHAR(50) PRIMARY KEY,
    request_date DATE NOT NULL,
    package_type VARCHAR(10) NOT NULL CHECK (package_type IN ('소', '중', '대')),
    qty INTEGER NOT NULL,
    address VARCHAR(255) NOT NULL,
    recipient VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    remark TEXT,
    dispatch_date DATE NULL,
    status VARCHAR(20) NULL CHECK (status IN ('대기', '회수중', '회수완료', '이슈')),
    reason TEXT NULL
);