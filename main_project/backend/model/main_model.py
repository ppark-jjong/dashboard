#MAIN_PROJECT/backend/model/main_model.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Driver(Base):
    __tablename__ = 'driver'
    __table_args__ = {'schema': 'delivery_system'}

    driver = Column(Integer, primary_key=True, autoincrement=True)
    driver_name = Column(String(45), nullable=False)
    driver_contact = Column(String(20), nullable=False)
    driver_region = Column(String(20), nullable=False)

class PostalCode(Base):
    __tablename__ = 'postal_code'
    __table_args__ = {'schema': 'delivery_system'}

    postal_code = Column(String(10), primary_key=True)
    duration_time = Column(Integer, nullable=True)
    distance = Column(Integer, nullable=True)
    city = Column(String(45), nullable=True)
    district = Column(String(45), nullable=True)

class Delivery(Base):
    __tablename__ = 'delivery'
    __table_args__ = {'schema': 'delivery_system'}

    dps = Column(String(50), primary_key=True)
    department = Column(String(100), nullable=False)
    warehouse = Column(String(45), nullable=True)
    sla = Column(String(20), nullable=False)
    eta = Column(DateTime, nullable=True)
    status = Column(String(10), nullable=False, default='대기')
    dispatch_time = Column(DateTime, nullable=True)
    depart_time = Column(DateTime, nullable=True)
    completed_time = Column(DateTime, nullable=True)
    postal_code = Column(String(10), ForeignKey('delivery_system.postal_code.postal_code', ondelete='SET NULL'), nullable=True)
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=True)
    remark = Column(Text, nullable=True)
    driver = Column(Integer, ForeignKey('delivery_system.driver.driver', ondelete='SET NULL'), nullable=True)

class Return(Base):
    __tablename__ = 'return'
    __table_args__ = {'schema': 'delivery_system'}

    dps = Column(String(50), primary_key=True)
    department = Column(String(45), nullable=False)
    eta = Column(DateTime, nullable=True)
    package_type = Column(String(10), nullable=True)
    qty = Column(Integer, nullable=True)
    status = Column(String(10), nullable=False, default='대기')
    address = Column(String(255), nullable=False)
    customer = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=True)
    remark = Column(Text, nullable=True)
    dispatch_date = Column(DateTime, nullable=True)
    driver = Column(Integer, ForeignKey('delivery_system.driver.driver', ondelete='SET NULL'), nullable=True)
    postal_code = Column(String(10), ForeignKey('delivery_system.postal_code.postal_code', ondelete='SET NULL'), nullable=True)