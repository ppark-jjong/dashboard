# src/model/main_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Driver(Base):
    __tablename__ = "driver"

    driver = Column(Integer, primary_key=True, autoincrement=True)
    driver_name = Column(String(45), nullable=False)
    driver_contact = Column(String(20), nullable=False)
    driver_region = Column(String(20), nullable=False)

    deliveries = relationship("Delivery", back_populates="driver_rel")
    returns = relationship("Return", back_populates="driver_rel")

class PostalCode(Base):
    __tablename__ = 'postal_code'

    postal_code = Column(String(10), primary_key=True)
    duration_time = Column(Integer, nullable=True, default=None)
    distance = Column(Integer, nullable=True, default=None)
    city = Column(String(45), nullable=True, default=None)
    district = Column(String(45), nullable=True, default=None)

    deliveries = relationship('Delivery', back_populates='postal_code_rel', lazy='select')
    returns = relationship('Return', back_populates='postal_code_rel', lazy='select')

class Dashboard(Base):
    __tablename__ = "dashboard"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(10), nullable=False)  # 'delivery' or 'return'
    dps = Column(String(50), nullable=False, unique=True)
    status = Column(String(10), nullable=False, default='대기')
    driver = Column(Integer, ForeignKey('driver.driver'), nullable=True)
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'), nullable=False)
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20))
    remark = Column(Text)
    eta = Column(DateTime)
    depart_time = Column(DateTime)
    completed_time = Column(DateTime)

    delivery = relationship("Delivery", back_populates="dashboard_rel", uselist=False)
    return_item = relationship("Return", back_populates="dashboard_rel", uselist=False)

class Delivery(Base):
    __tablename__ = "delivery"

    department = Column(String(100), nullable=False)
    warehouse = Column(String(45))
    dps = Column(String(50), primary_key=True)
    sla = Column(String(20), nullable=False)
    eta = Column(DateTime)
    status = Column(String(10), nullable=False, default='대기')
    depart_time = Column(DateTime)
    completed_time = Column(DateTime)
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'))
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20))
    remark = Column(Text)
    driver = Column(Integer, ForeignKey('driver.driver'))
    dashboard_id = Column(Integer, ForeignKey('dashboard.id'))

    driver_rel = relationship("Driver", back_populates="deliveries")
    postal_code_rel = relationship("PostalCode", back_populates="deliveries")
    dashboard_rel = relationship("Dashboard", back_populates="delivery")

class Return(Base):
    __tablename__ = "return"

    department = Column(String(45), nullable=False)
    dps = Column(String(50), primary_key=True)
    eta = Column(DateTime)
    package_type = Column(String(10))
    qty = Column(Integer)
    status = Column(String(10), nullable=False, default='대기')
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20))
    remark = Column(Text)
    driver = Column(Integer, ForeignKey('driver.driver'))
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'))
    dashboard_id = Column(Integer, ForeignKey('dashboard.id'))

    driver_rel = relationship("Driver", back_populates="returns")
    postal_code_rel = relationship("PostalCode", back_populates="returns")
    dashboard_rel = relationship("Dashboard", back_populates="return_item")