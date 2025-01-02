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
  `driver` INT NOT NULL,
  `driver_name` VARCHAR(45) NULL DEFAULT NULL,
  `driver_contact` VARCHAR(20) NULL DEFAULT NULL,
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
  PRIMARY KEY (`postal_code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `delivery_system`.`delivery`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `delivery_system`.`delivery` (
  `dashboard_id` INT NULL DEFAULT NULL,
  `department` VARCHAR(100) NOT NULL,
  `warehouse` VARCHAR(45) NULL DEFAULT NULL,
  `dps` VARCHAR(50) NOT NULL,
  `sla` VARCHAR(20) NOT NULL,
  `eta` DATETIME NULL DEFAULT NULL,
  `status` VARCHAR(20) NULL DEFAULT NULL,
  `dispatch_time` DATETIME NULL DEFAULT NULL,
  `depart_time` DATETIME NULL DEFAULT NULL,
  `completed_time` DATETIME NULL DEFAULT NULL,
  `postal_code` VARCHAR(10) NULL DEFAULT NULL,
  `address` VARCHAR(255) NULL DEFAULT NULL,
  `customer` VARCHAR(100) NULL DEFAULT NULL,
  `contact` VARCHAR(20) NULL DEFAULT NULL,
  `remark` TEXT NULL DEFAULT NULL,
  `driver` INT NULL DEFAULT NULL,
  PRIMARY KEY (`dps`),
  INDEX `fk_delivery_postal_code_idx` (`postal_code` ASC) VISIBLE,
  INDEX `fk_delivery_driver_idx` (`driver` ASC) VISIBLE,
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
  `eta` DATE NOT NULL,
  `package_type` VARCHAR(10) NOT NULL,
  `qty` INT NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  `recipient` VARCHAR(100) NOT NULL,
  `contact` VARCHAR(20) NOT NULL,
  `remark` TEXT NULL DEFAULT NULL,
  `dispatch_date` DATE NULL DEFAULT NULL,
  `status` VARCHAR(20) NULL DEFAULT NULL,
  `dashboard_id` INT NULL DEFAULT NULL,
  `driver` INT NULL DEFAULT NULL,
  PRIMARY KEY (`dps`),
  INDEX `fk_return_driver_idx` (`driver` ASC) VISIBLE,
  CONSTRAINT `fk_return_driver`
    FOREIGN KEY (`driver`)
    REFERENCES `delivery_system`.`driver` (`driver`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
