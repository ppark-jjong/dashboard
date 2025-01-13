# src/model/main_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


# Enum 클래스 정의
class TaskType(enum.Enum):
    delivery = 'delivery'
    return_ = 'return'  # return은 예약어라 return_로 정의


class Driver(Base):
    __tablename__ = "driver"

    driver = Column(Integer, primary_key=True, autoincrement=True)
    driver_name = Column(String(45), nullable=False)
    driver_contact = Column(String(20), nullable=False)
    driver_region = Column(String(20), nullable=False)

    deliveries = relationship("Delivery", back_populates="driver_rel")
    returns = relationship("Return", back_populates="driver_rel")
    dashboard_tasks = relationship("Dashboard", back_populates="driver_rel")


class PostalCode(Base):
    __tablename__ = 'postal_code'

    postal_code = Column(String(10), primary_key=True)
    duration_time = Column(Integer, nullable=True)
    distance = Column(Integer, nullable=True)
    city = Column(String(45), nullable=True)
    district = Column(String(45), nullable=True)

    deliveries = relationship('Delivery', back_populates='postal_code_rel')
    returns = relationship('Return', back_populates='postal_code_rel')
    dashboard_tasks = relationship('Dashboard', back_populates='postal_code_rel')


class Dashboard(Base):
    __tablename__ = "dashboard"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(SQLAlchemyEnum(TaskType), nullable=False)  # SQLAlchemy Enum 사용
    dps = Column(String(50), nullable=False, unique=True)
    status = Column(String(10), nullable=False, default='대기')

    # 기본 정보
    department = Column(String(100), nullable=False)
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'))
    district = Column(String(45))
    duration_time = Column(Integer)
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20))
    remark = Column(Text)

    # 시간 정보
    eta = Column(DateTime)
    depart_time = Column(DateTime)
    completed_time = Column(DateTime)

    # 기사 정보
    driver_id = Column(Integer, ForeignKey('driver.driver'))
    driver_name = Column(String(45))
    driver_contact = Column(String(20))

    # delivery 전용 필드
    warehouse = Column(String(45))
    sla = Column(String(20))

    driver_rel = relationship("Driver", back_populates="dashboard_tasks")
    postal_code_rel = relationship("PostalCode", back_populates="dashboard_tasks")


class Delivery(Base):
    __tablename__ = "delivery"

    dps = Column(String(50), primary_key=True)
    department = Column(String(100), nullable=False)
    warehouse = Column(String(45))
    sla = Column(String(20), nullable=False)
    eta = Column(DateTime)
    status = Column(String(10), nullable=False, default='대기')
    dispatch_time = Column(DateTime)
    depart_time = Column(DateTime)
    completed_time = Column(DateTime)
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'))
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20))
    remark = Column(Text)
    driver = Column(Integer, ForeignKey('driver.driver'))

    driver_rel = relationship("Driver", back_populates="deliveries")
    postal_code_rel = relationship("PostalCode", back_populates="deliveries")


class Return(Base):
    __tablename__ = "return"

    dps = Column(String(50), primary_key=True)
    department = Column(String(45), nullable=False)
    eta = Column(DateTime)
    package_type = Column(String(10))
    qty = Column(Integer)
    status = Column(String(10), nullable=False, default='대기')
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'))
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20))
    remark = Column(Text)
    dispatch_date = Column(Date)
    driver = Column(Integer, ForeignKey('driver.driver'))

    driver_rel = relationship("Driver", back_populates="returns")
    postal_code_rel = relationship("PostalCode", back_populates="returns")