from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()


class Driver(Base):
    __tablename__ = "driver"
    __table_args__ = {"schema": "delivery_system"}

    driver = Column(
        Integer, primary_key=True, autoincrement=True, comment="드라이버 고유 ID"
    )
    driver_name = Column(String(45), nullable=False, comment="드라이버 이름")
    driver_contact = Column(
        String(20), nullable=False, comment="드라이버 연락처 (전화번호)"
    )
    driver_region = Column(
        String(20), nullable=False, comment="드라이버가 담당하는 지역"
    )

    # Relationships
    deliveries = relationship("Delivery", back_populates="driver_info")
    returns = relationship("Return", back_populates="driver_info")


class PostalCode(Base):
    __tablename__ = "postal_code"
    __table_args__ = {"schema": "delivery_system"}

    postal_code = Column(String(10), primary_key=True, comment="우편번호")
    duration_time = Column(Integer, nullable=True, comment="예상 소요 시간 (분)")
    distance = Column(Integer, nullable=True, comment="예상 거리 (km)")
    city = Column(String(45), nullable=True, comment="도시 정보")
    district = Column(String(45), nullable=True, comment="행정 구역 정보")

    # Relationships
    deliveries = relationship("Delivery", back_populates="postal_code_info")
    returns = relationship("Return", back_populates="postal_code_info")


class Dashboard(Base):
    __tablename__ = "dashboard"
    __table_args__ = {
        "schema": "delivery_system",
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_0900_ai_ci",
    }

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="대시보드 작업 고유 ID"
    )
    type = Column(
        SQLEnum("delivery", "return", name="task_type"),
        nullable=False,
        comment="작업 유형",
    )
    status = Column(String(10), nullable=False, default="대기", comment="작업 상태")
    driver_id = Column(Integer, nullable=False, comment="배정된 드라이버의 ID")
    driver_name = Column(String(45), nullable=False, comment="배정된 드라이버 이름")
    department = Column(String(100), nullable=False, comment="작업의 담당 부서")
    postal_code = Column(
        String(10), nullable=False, comment="작업 대상 지역의 우편번호"
    )
    region = Column(
        String(45), nullable=True, comment="도시와 행정 구역 정보를 조합한 지역명"
    )
    duration_time = Column(Integer, nullable=True, comment="예상 소요 시간 (분)")
    address = Column(String(255), nullable=False, comment="배송 또는 반품지 주소")
    customer = Column(String(100), nullable=False, comment="고객 이름")
    contact = Column(String(20), nullable=True, comment="고객 연락처")
    remark = Column(Text, nullable=True, comment="작업 관련 비고 사항")
    eta = Column(DateTime, nullable=True, comment="도착 예정 시간")
    depart_time = Column(DateTime, nullable=True, comment="출발 시간")
    completed_time = Column(DateTime, nullable=True, comment="작업 완료 시간")
    driver_contact = Column(String(20), nullable=True, comment="배정된 드라이버 연락처")
    sla = Column(String(20), nullable=True, comment="서비스 수준 계약(SLA)")
    warehouse = Column(String(45), nullable=True, comment="작업의 창고 이름")
    dps = Column(String(50), nullable=True, comment="DPS 코드")


class Delivery(Base):
    __tablename__ = "delivery"
    __table_args__ = {"schema": "delivery_system"}

    department = Column(String(100), nullable=False, comment="담당 부서")
    warehouse = Column(String(45), nullable=True, comment="창고 이름")
    dps = Column(String(50), primary_key=True, comment="DPS 코드")
    sla = Column(String(20), nullable=False, comment="서비스 수준 계약(SLA)")
    eta = Column(DateTime, nullable=True, comment="도착 예정 시간")
    status = Column(String(10), nullable=False, default="대기", comment="작업 상태")
    dispatch_time = Column(DateTime, nullable=True, comment="디스패치 시간")
    depart_time = Column(DateTime, nullable=True, comment="출발 시간")
    completed_time = Column(DateTime, nullable=True, comment="작업 완료 시간")
    postal_code = Column(
        String(10),
        ForeignKey(
            "delivery_system.postal_code.postal_code",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
    )
    address = Column(String(255), nullable=False, comment="배송지 주소")
    customer = Column(String(100), nullable=False, comment="고객 이름")
    contact = Column(String(20), nullable=True, comment="고객 연락처")
    remark = Column(Text, nullable=True, comment="비고 사항")
    driver = Column(
        Integer,
        ForeignKey(
            "delivery_system.driver.driver", ondelete="SET NULL", onupdate="CASCADE"
        ),
        nullable=True,
    )
    dashboard_id = Column(Integer, nullable=True, comment="연관된 대시보드 ID")

    # Relationships
    driver_info = relationship("Driver", back_populates="deliveries")
    postal_code_info = relationship("PostalCode", back_populates="deliveries")


class Return(Base):
    __tablename__ = "return"
    __table_args__ = {"schema": "delivery_system"}

    department = Column(String(45), nullable=False, comment="담당 부서")
    dps = Column(String(50), primary_key=True, comment="DPS 코드")
    eta = Column(DateTime, nullable=True, comment="도착 예정 시간")
    package_type = Column(String(10), nullable=True, comment="패키지 유형")
    qty = Column(Integer, nullable=True, comment="패키지 수량")
    status = Column(String(10), nullable=False, default="대기", comment="작업 상태")
    address = Column(String(255), nullable=False, comment="반품지 주소")
    customer = Column(String(100), nullable=False, comment="고객 이름")
    contact = Column(String(20), nullable=True, comment="고객 연락처")
    remark = Column(Text, nullable=True, comment="비고 사항")
    dispatch_date = Column(DateTime, nullable=True, comment="디스패치 날짜")
    driver = Column(
        Integer,
        ForeignKey(
            "delivery_system.driver.driver", ondelete="SET NULL", onupdate="CASCADE"
        ),
        nullable=True,
    )
    postal_code = Column(
        String(10),
        ForeignKey(
            "delivery_system.postal_code.postal_code",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
    )
    dashboard_id = Column(Integer, nullable=True, comment="연관된 대시보드 ID")

    # Relationships
    driver_info = relationship("Driver", back_populates="returns")
    postal_code_info = relationship("PostalCode", back_populates="returns")
