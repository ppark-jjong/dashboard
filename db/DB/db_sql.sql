-- -----------------------------------------------------
-- Schema delivery_system
-- 배송 시스템 관리용 데이터베이스
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `delivery_system` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `delivery_system`;

-- -----------------------------------------------------
-- Table `delivery_system`.`driver`
-- 배송 기사 정보 테이블
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`driver` (
  `driver` INT NOT NULL AUTO_INCREMENT COMMENT '드라이버 고유 ID',
  `driver_name` VARCHAR(45) NOT NULL COMMENT '드라이버 이름',
  `driver_contact` VARCHAR(20) NOT NULL COMMENT '드라이버 연락처 (전화번호)',
  `driver_region` VARCHAR(20) NOT NULL COMMENT '드라이버가 담당하는 지역',
  PRIMARY KEY (`driver`)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `delivery_system`.`postal_code`
-- 우편번호 정보 테이블
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`postal_code` (
  `postal_code` VARCHAR(10) NOT NULL COMMENT '우편번호',
  `duration_time` INT NULL DEFAULT NULL COMMENT '예상 소요 시간 (분)',
  `distance` INT NULL DEFAULT NULL COMMENT '예상 거리 (km)',
  `city` VARCHAR(45) NULL DEFAULT NULL COMMENT '도시 정보',
  `district` VARCHAR(45) NULL DEFAULT NULL COMMENT '행정 구역 정보',
  PRIMARY KEY (`postal_code`)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `delivery_system`.`dashboard`
-- 작업 대시보드 테이블 (외래키 제거 및 컬럼 설명 추가)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`dashboard` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '대시보드 작업 고유 ID',
  
  -- 중복 저장: 작업 유형을 구분 (배송 또는 반품)
  `type` ENUM('delivery', 'return') NOT NULL COMMENT '작업 유형 (delivery_system.delivery 또는 delivery_system.return의 작업 유형을 구분)',
  
  -- 중복 저장: 작업 상태를 캐싱 (예: 대기, 완료)
  `status` VARCHAR(10) NOT NULL DEFAULT '대기' COMMENT '작업 상태 (delivery_system.delivery.status 또는 delivery_system.return.status와 동일)',
  
  -- 중복 저장: driver 테이블의 driver 컬럼
  `driver_id` INT NOT NULL COMMENT '배정된 드라이버의 ID (delivery_system.driver.driver와 동일)',
  
  -- 중복 저장: driver 테이블의 driver_name 컬럼
  `driver_name` VARCHAR(45) NOT NULL COMMENT '배정된 드라이버 이름 (delivery_system.driver.driver_name을 캐싱)',
  
  -- 중복 저장: delivery 또는 return 테이블의 department 컬럼
  `department` VARCHAR(100) NOT NULL COMMENT '작업의 담당 부서 (delivery_system.delivery.department 또는 delivery_system.return.department와 동일)',
  
  -- 중복 저장: postal_code 테이블의 postal_code 컬럼
  `postal_code` VARCHAR(10) NOT NULL COMMENT '작업 대상 지역의 우편번호 (delivery_system.postal_code.postal_code와 동일)',
  
  -- 파생 데이터: postal_code 테이블의 city와 district를 합친 정보
  `region` VARCHAR(45) NULL DEFAULT NULL COMMENT '도시와 행정 구역 정보를 조합한 지역명 (delivery_system.postal_code.city + delivery_system.postal_code.district)',
  
  -- 중복 저장: postal_code 테이블의 duration_time 컬럼
  `duration_time` INT NULL DEFAULT NULL COMMENT '예상 소요 시간 (분) (delivery_system.postal_code.duration_time과 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 address 컬럼
  `address` VARCHAR(255) NOT NULL COMMENT '배송 또는 반품지 주소 (delivery_system.delivery.address 또는 delivery_system.return.address와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 customer 컬럼
  `customer` VARCHAR(100) NOT NULL COMMENT '고객 이름 (delivery_system.delivery.customer 또는 delivery_system.return.customer와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 contact 컬럼
  `contact` VARCHAR(20) NULL DEFAULT NULL COMMENT '고객 연락처 (delivery_system.delivery.contact 또는 delivery_system.return.contact와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 remark 컬럼
  `remark` TEXT NULL DEFAULT NULL COMMENT '작업 관련 비고 사항 (delivery_system.delivery.remark 또는 delivery_system.return.remark와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 eta 컬럼
  `eta` DATETIME NULL DEFAULT NULL COMMENT '도착 예정 시간 (delivery_system.delivery.eta 또는 delivery_system.return.eta와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 depart_time 컬럼
  `depart_time` DATETIME NULL DEFAULT NULL COMMENT '출발 시간 (delivery_system.delivery.depart_time 또는 delivery_system.return.depart_time와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 completed_time 컬럼
  `completed_time` DATETIME NULL DEFAULT NULL COMMENT '작업 완료 시간 (delivery_system.delivery.completed_time 또는 delivery_system.return.completed_time와 동일)',
  
  -- 중복 저장: driver 테이블의 driver_contact 컬럼
  `driver_contact` VARCHAR(20) NULL DEFAULT NULL COMMENT '배정된 드라이버 연락처 (delivery_system.driver.driver_contact을 캐싱)',
  
  -- 중복 저장: delivery 또는 return 테이블의 sla 컬럼
  `sla` VARCHAR(20) NULL DEFAULT NULL COMMENT '서비스 수준 계약(SLA) (delivery_system.delivery.sla 또는 delivery_system.return.sla와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 warehouse 컬럼
  `warehouse` VARCHAR(45) NULL DEFAULT NULL COMMENT '작업의 창고 이름 (delivery_system.delivery.warehouse 또는 delivery_system.return.warehouse와 동일)',
  
  -- 중복 저장: delivery 또는 return 테이블의 dps 컬럼
  `dps` VARCHAR(50) NULL DEFAULT NULL COMMENT 'DPS (Dynamic Parcel Sortation) 코드 (delivery_system.delivery.dps 또는 delivery_system.return.dps와 동일)',

  
  PRIMARY KEY (`id`),
  
  -- 인덱스 설정
  UNIQUE INDEX `unique_task` (`type` ASC),
  INDEX `idx_status_driver` (`status` ASC, `driver_id` ASC),
  INDEX `idx_postal_code` (`postal_code` ASC)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `delivery_system`.`delivery`
-- 배송 작업 상세 정보 테이블
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`delivery` (
  `department` VARCHAR(100) NOT NULL COMMENT '담당 부서',
  `warehouse` VARCHAR(45) NULL DEFAULT NULL COMMENT '창고 이름',
  `dps` VARCHAR(50) NOT NULL COMMENT 'DPS (Dynamic Parcel Sortation) 코드 - 고유값',
  `sla` VARCHAR(20) NOT NULL COMMENT '서비스 수준 계약(SLA)',
  `eta` DATETIME NULL DEFAULT NULL COMMENT '도착 예정 시간',
  `status` VARCHAR(10) NOT NULL DEFAULT '대기' COMMENT '작업 상태',
  `dispatch_time` DATETIME NULL DEFAULT NULL COMMENT '디스패치 시간',
  `depart_time` DATETIME NULL DEFAULT NULL COMMENT '출발 시간',
  `completed_time` DATETIME NULL DEFAULT NULL COMMENT '작업 완료 시간',
  `postal_code` VARCHAR(10) NULL DEFAULT NULL COMMENT '배송지 우편번호',
  `address` VARCHAR(255) NOT NULL COMMENT '배송지 주소',
  `customer` VARCHAR(100) NOT NULL COMMENT '고객 이름',
  `contact` VARCHAR(20) NULL DEFAULT NULL COMMENT '고객 연락처',
  `remark` TEXT NULL DEFAULT NULL COMMENT '비고 사항',
  `driver` INT NULL DEFAULT NULL COMMENT '배정된 드라이버 ID',
  `dashboard_id` INT NULL DEFAULT NULL COMMENT '연관된 대시보드 ID',
  PRIMARY KEY (`dps`),
  INDEX `idx_driver` (`driver` ASC),
  INDEX `idx_postal_code` (`postal_code` ASC),
  CONSTRAINT `fk_delivery_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `delivery_system`.`driver` (`driver`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_delivery_postal_code`
    FOREIGN KEY (`postal_code`)
    REFERENCES `delivery_system`.`postal_code` (`postal_code`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `delivery_system`.`return`
-- 반품 작업 상세 정보 테이블
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`return` (
  `department` VARCHAR(45) NOT NULL COMMENT '담당 부서',
  `dps` VARCHAR(50) NOT NULL COMMENT 'DPS (Dynamic Parcel Sortation) 코드 - 고유값',
  `eta` DATETIME NULL DEFAULT NULL COMMENT '도착 예정 시간',
  `package_type` VARCHAR(10) NULL DEFAULT NULL COMMENT '패키지 유형 (예: 소형, 대형)',
  `qty` INT NULL DEFAULT NULL COMMENT '패키지 수량',
  `status` VARCHAR(10) NOT NULL DEFAULT '대기' COMMENT '작업 상태',
  `address` VARCHAR(255) NOT NULL COMMENT '반품지 주소',
  `customer` VARCHAR(100) NOT NULL COMMENT '고객 이름',
  `contact` VARCHAR(20) NULL DEFAULT NULL COMMENT '고객 연락처',
  `remark` TEXT NULL DEFAULT NULL COMMENT '비고 사항',
  `dispatch_date` DATE NULL DEFAULT NULL COMMENT '디스패치 날짜',
  `driver` INT NULL DEFAULT NULL COMMENT '배정된 드라이버 ID',
  `postal_code` VARCHAR(10) NULL DEFAULT NULL COMMENT '반품지 우편번호',
  `dashboard_id` INT NULL DEFAULT NULL COMMENT '연관된 대시보드 ID',
  PRIMARY KEY (`dps`),
  INDEX `idx_driver` (`driver` ASC),
  INDEX `idx_postal_code` (`postal_code` ASC),
  CONSTRAINT `fk_return_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `delivery_system`.`driver` (`driver`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_return_postal_code`
    FOREIGN KEY (`postal_code`)
    REFERENCES `delivery_system`.`postal_code` (`postal_code`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
