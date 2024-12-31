-- -----------------------------------------------------
-- 스키마 및 초기 설정
-- -----------------------------------------------------
/*  
   아래 설정은 스키마 생성 전에 외래키/고유키 제약을 잠시 해제한 후,
   작업이 끝나면 다시 복원하기 위함임
*/
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS;
SET UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS;
SET FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE;
SET SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- 스키마 생성
-- -----------------------------------------------------
/*  
   delivery_system이라는 스키마(데이터베이스)를 생성하고 사용함
*/
CREATE SCHEMA IF NOT EXISTS `delivery_system` 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_0900_ai_ci;

USE `delivery_system`;

-- -----------------------------------------------------
-- 테이블: postal_code
-- -----------------------------------------------------
/*
   - 우편번호별로 거리/시간 정보를 저장
   - primary key: postal_code
*/
CREATE TABLE IF NOT EXISTS `postal_code` (
  `postal_code` VARCHAR(10) NOT NULL,
  `duration_time` INT NULL,
  `distance` INT(5) NULL,
  PRIMARY KEY (`postal_code`)
)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- 테이블: driver
-- -----------------------------------------------------
/*
   - 기사 정보를 저장하는 테이블
   - primary key: driver (일종의 기사ID)
*/
CREATE TABLE IF NOT EXISTS `driver` (
  `driver` INT NOT NULL,
  `driver_name` VARCHAR(45) NULL,
  `driver_contact` VARCHAR(20) NULL,
  PRIMARY KEY (`driver`)
)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- 테이블: dashboard
-- -----------------------------------------------------
/*
   - 실제 운영에서 redis로 캐시/관리할 예정이나,
     테스트를 위해 DB에도 생성
   - primary key: dashboard_id
   - driver_driver는 driver 테이블과 FK로 연결
   - department, type, driver_driver (기사 정보) 저장
*/
CREATE TABLE IF NOT EXISTS `dashboard` (
  `dashboard_id` INT NOT NULL,
  `department` VARCHAR(45) NULL,
  `type` VARCHAR(45) NULL,
  `driver_driver` INT NOT NULL,
  PRIMARY KEY (`dashboard_id`),
  INDEX `fk_dashboard_driver1_idx` (`driver_driver` ASC) VISIBLE,
  CONSTRAINT `fk_dashboard_driver1`
    FOREIGN KEY (`driver_driver`)
    REFERENCES `driver` (`driver`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- 테이블: delivery
-- -----------------------------------------------------
/*
   - 배송 관련 정보 테이블
   - PK: dps (개별 배송 건을 고유 식별)
   - dashboard_id 로 dashboard 테이블과 연결
   - postal_code 로 postal_code 테이블과 연결
   - status를 INT -> VARCHAR(20)로 변경 (회수 테이블과 통일)
   - driver 칼럼을 추가해서 기사 정보를 직접 저장 
     (dashboard와 동기화 예정)
*/
CREATE TABLE IF NOT EXISTS `delivery` (
  `dashboard_id` INT NOT NULL,
  `department` VARCHAR(100) NOT NULL,
  `warehouse` VARCHAR(45) NULL,
  `dps` VARCHAR(50) NOT NULL,      -- PK
  `sla` TINYINT(4) NOT NULL,
  `eta` DATETIME NULL,             -- 배송 ETA
  `status` VARCHAR(20) NULL,       -- 상태 (문자열)
  `dispatch_time` DATETIME NULL,
  `depart_time` DATETIME NULL DEFAULT NULL,
  `completed_time` DATETIME NULL DEFAULT NULL,  -- 기존 오타(complted)를 수정
  `postal_code` VARCHAR(10) NOT NULL,
  `address` VARCHAR(255) NULL,
  `customer` VARCHAR(100) NULL,
  `contact` VARCHAR(20) NULL,
  `remark` TEXT NULL DEFAULT NULL,
  `driver` INT NULL,               -- 새로 추가 (기사 ID)
  PRIMARY KEY (`dps`),

  -- FK 연결
  INDEX `fk_delivery_dashboard_idx` (`dashboard_id` ASC) VISIBLE,
  INDEX `fk_delivery_postal_code_idx` (`postal_code` ASC) VISIBLE,
  INDEX `fk_delivery_driver_idx` (`driver` ASC) VISIBLE,

  CONSTRAINT `fk_delivery_dashboard`
    FOREIGN KEY (`dashboard_id`)
    REFERENCES `dashboard` (`dashboard_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,

  CONSTRAINT `fk_delivery_postal_code`
    FOREIGN KEY (`postal_code`)
    REFERENCES `postal_code` (`postal_code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,

  CONSTRAINT `fk_delivery_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `driver` (`driver`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- 테이블: return
-- -----------------------------------------------------
/*
   - 회수(반품) 관련 정보 테이블
   - PK: dps (개별 회수 건을 고유 식별)
   - dashboard_id 로 dashboard 테이블과 연결
   - request_date를 eta로 변경하여 동일하게 사용
   - driver 칼럼 추가 (배차 기사 동기화)
   - SLA는 없음 (회수 업무에는 불필요하다는 요구사항)
   - status: VARCHAR(20) 유지 (delivery와 통일)
*/
CREATE TABLE IF NOT EXISTS `return` (
  `department` VARCHAR(45) NOT NULL,
  `dps` VARCHAR(50) NOT NULL,
  `eta` DATE NOT NULL,             -- request_date -> eta 로 변경
  `package_type` VARCHAR(10) NOT NULL,
  `qty` INT NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  `recipient` VARCHAR(100) NOT NULL,   -- 회수 시 수령인(기존 'customer'와 다른 명칭)
  `contact` VARCHAR(20) NOT NULL,
  `remark` TEXT NULL DEFAULT NULL,
  `dispatch_date` DATE NULL DEFAULT NULL,
  `status` VARCHAR(20) NULL DEFAULT NULL,
  `dashboard_id` INT NOT NULL,
  `driver` INT NULL,                  -- 새로 추가 (기사 ID)
  PRIMARY KEY (`dps`),

  -- FK 연결
  INDEX `fk_return_dashboard_idx` (`dashboard_id` ASC) VISIBLE,
  INDEX `fk_return_driver_idx` (`driver` ASC) VISIBLE,

  CONSTRAINT `fk_return_dashboard`
    FOREIGN KEY (`dashboard_id`)
    REFERENCES `dashboard` (`dashboard_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,

  CONSTRAINT `fk_return_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `driver` (`driver`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- 마무리 설정 복원
-- -----------------------------------------------------
/*
   처음 해제했던 제약 사항을 복원
*/
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
