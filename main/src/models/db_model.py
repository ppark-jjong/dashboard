from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PostalCode(Base):
    __tablename__ = 'postal_code'

    postal_code = Column(String(10), primary_key=True)
    duration_time = Column(Integer, nullable=True)
    distance = Column(Integer, nullable=True)

    deliveries = relationship("Delivery", back_populates="postal_code_info")

class Driver(Base):
    __tablename__ = 'driver'

    driver = Column(Integer, primary_key=True)
    driver_name = Column(String(45), nullable=True)
    driver_contact = Column(String(20), nullable=True)

    deliveries = relationship("Delivery", back_populates="driver_info")
    returns = relationship("Return", back_populates="driver_info")
    dashboards = relationship("Dashboard", back_populates="driver_info")

class Dashboard(Base):
    __tablename__ = 'dashboard'

    dashboard_id = Column(Integer, primary_key=True)
    department = Column(String(45), nullable=True)
    type = Column(String(45), nullable=True)
    driver = Column(Integer, ForeignKey('driver.driver'), nullable=False)

    driver_info = relationship("Driver", back_populates="dashboards")
    deliveries = relationship("Delivery", back_populates="dashboard")
    returns = relationship("Return", back_populates="dashboard")

class Delivery(Base):
    __tablename__ = 'delivery'

    dashboard_id = Column(Integer, ForeignKey('dashboard.dashboard_id'), nullable=False)
    department = Column(String(100), nullable=False)
    warehouse = Column(String(45), nullable=True)
    dps = Column(String(50), primary_key=True)
    sla = Column(String(20), nullable=False)  # Changed to String(20)
    eta = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=True)
    dispatch_time = Column(DateTime, nullable=True)
    depart_time = Column(DateTime, nullable=True)
    completed_time = Column(DateTime, nullable=True)
    postal_code = Column(String(10), ForeignKey('postal_code.postal_code'), nullable=False)
    address = Column(String(255), nullable=True)
    customer = Column(String(100), nullable=True)
    contact = Column(String(20), nullable=True)
    remark = Column(Text, nullable=True)
    driver = Column(Integer, ForeignKey('driver.driver'), nullable=True)

    dashboard = relationship("Dashboard", back_populates="deliveries")
    driver_info = relationship("Driver", back_populates="deliveries")
    postal_code_info = relationship("PostalCode", back_populates="deliveries")

class Return(Base):
    __tablename__ = 'return'

    department = Column(String(45), nullable=False)
    dps = Column(String(50), primary_key=True)
    eta = Column(Date, nullable=False)
    package_type = Column(String(10), nullable=False)
    qty = Column(Integer, nullable=False)
    address = Column(String(255), nullable=False)
    recipient = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=False)
    remark = Column(Text, nullable=True)
    dispatch_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=True)
    dashboard_id = Column(Integer, ForeignKey('dashboard.dashboard_id'), nullable=False)
    driver = Column(Integer, ForeignKey('driver.driver'), nullable=True)

    dashboard = relationship("Dashboard", back_populates="returns")
    driver_info = relationship("Driver", back_populates="returns")