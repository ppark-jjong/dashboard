-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema delivery_system
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema delivery_system
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `delivery_system` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `delivery_system` ;

-- -----------------------------------------------------
-- Table `delivery_system`.`driver`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`driver` (
  `driver` INT NOT NULL AUTO_INCREMENT,
  `driver_name` VARCHAR(45) NOT NULL,
  `driver_contact` VARCHAR(20) NOT NULL,
  `driver_region` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`driver`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `delivery_system`.`postal_code`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`postal_code` (
  `postal_code` VARCHAR(10) NOT NULL,
  `duration_time` INT NULL DEFAULT NULL,
  `distance` INT NULL DEFAULT NULL,
  `city` VARCHAR(45) NULL DEFAULT NULL,
  `district` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`postal_code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `delivery_system`.`dashboard`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`dashboard` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '대시보드 ID',
  `type` VARCHAR(10) NOT NULL COMMENT '작업 유형 (배송 또는 반품)',
  `dps` VARCHAR(50) NOT NULL COMMENT '배송/반품 ID',
  `status` VARCHAR(10) NOT NULL DEFAULT '대기' COMMENT '배송 상태',
  `driver` INT NULL DEFAULT NULL COMMENT '배정된 드라이버',
  `postal_code` VARCHAR(10) NOT NULL COMMENT '우편번호',
  `address` VARCHAR(255) NOT NULL COMMENT '배송지 주소',
  `customer` VARCHAR(100) NOT NULL COMMENT '고객명',
  `contact` VARCHAR(20) NULL DEFAULT NULL COMMENT '고객 연락처',
  `remark` TEXT NULL DEFAULT NULL COMMENT '비고',
  `depart_time` DATETIME NULL DEFAULT NULL COMMENT '배차 시간',
  `completed_time` DATETIME NULL DEFAULT NULL COMMENT '완료 시간',
  `eta` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `unique_dps` (`dps` ASC) VISIBLE,
  INDEX `idx_driver` (`driver` ASC) VISIBLE,
  INDEX `idx_postal_code` (`postal_code` ASC) VISIBLE,
  CONSTRAINT `fk_dashboard_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `delivery_system`.`driver` (`driver`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_dashboard_postal_code`
    FOREIGN KEY (`postal_code`)
    REFERENCES `delivery_system`.`postal_code` (`postal_code`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 82
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `delivery_system`.`delivery`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`delivery` (
  `department` VARCHAR(100) NOT NULL,
  `warehouse` VARCHAR(45) NULL DEFAULT NULL,
  `dps` VARCHAR(50) NOT NULL,
  `sla` VARCHAR(20) NOT NULL,
  `eta` DATETIME NULL DEFAULT NULL,
  `status` VARCHAR(10) NOT NULL DEFAULT '대기',
  `dispatch_time` DATETIME NULL DEFAULT NULL,
  `depart_time` DATETIME NULL DEFAULT NULL,
  `completed_time` DATETIME NULL DEFAULT NULL,
  `postal_code` VARCHAR(10) NULL DEFAULT NULL,
  `address` VARCHAR(255) NOT NULL,
  `customer` VARCHAR(100) NOT NULL,
  `contact` VARCHAR(20) NULL DEFAULT NULL,
  `remark` TEXT NULL DEFAULT NULL,
  `driver` INT NULL DEFAULT NULL,
  `dashboard_id` INT NULL DEFAULT NULL COMMENT '대시보드 ID',
  PRIMARY KEY (`dps`),
  INDEX `idx_driver` (`driver` ASC) VISIBLE,
  INDEX `idx_postal_code` (`postal_code` ASC) VISIBLE,
  INDEX `idx_dashboard_id` (`dashboard_id` ASC) VISIBLE,
  CONSTRAINT `fk_delivery_dashboard`
    FOREIGN KEY (`dashboard_id`)
    REFERENCES `delivery_system`.`dashboard` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_delivery_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `delivery_system`.`driver` (`driver`),
  CONSTRAINT `fk_delivery_postal_code`
    FOREIGN KEY (`postal_code`)
    REFERENCES `delivery_system`.`postal_code` (`postal_code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `delivery_system`.`return`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`return` (
  `department` VARCHAR(45) NOT NULL,
  `dps` VARCHAR(50) NOT NULL,
  `eta` DATETIME NULL DEFAULT NULL,
  `package_type` VARCHAR(10) NULL DEFAULT NULL,
  `qty` INT NULL DEFAULT NULL,
  `status` VARCHAR(10) NOT NULL DEFAULT '대기',
  `address` VARCHAR(255) NOT NULL,
  `customer` VARCHAR(100) NOT NULL,
  `contact` VARCHAR(20) NULL DEFAULT NULL,
  `remark` TEXT NULL DEFAULT NULL,
  `dispatch_date` DATE NULL DEFAULT NULL,
  `driver` INT NULL DEFAULT NULL,
  `postal_code` VARCHAR(10) NULL DEFAULT NULL,
  `dashboard_id` INT NULL DEFAULT NULL COMMENT '대시보드 ID',
  PRIMARY KEY (`dps`),
  INDEX `idx_driver` (`driver` ASC) VISIBLE,
  INDEX `idx_postal_code` (`postal_code` ASC) VISIBLE,
  INDEX `idx_dashboard_id` (`dashboard_id` ASC) VISIBLE,
  CONSTRAINT `fk_return_dashboard`
    FOREIGN KEY (`dashboard_id`)
    REFERENCES `delivery_system`.`dashboard` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_return_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `delivery_system`.`driver` (`driver`),
  CONSTRAINT `fk_return_postal_code`
    FOREIGN KEY (`postal_code`)
    REFERENCES `delivery_system`.`postal_code` (`postal_code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
