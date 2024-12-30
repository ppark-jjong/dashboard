from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class Delivery(db.Model):
    __tablename__ = 'delivery'

    # Primary Key
    dps = db.Column(db.String(50), primary_key=True)

    # Required fields
    eta = db.Column(db.DateTime, nullable=False)
    sla = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

    # Optional fields
    remark = db.Column(db.Text, nullable=True)
    depart_time = db.Column(db.DateTime, nullable=True)
    arrive_time = db.Column(db.DateTime, nullable=True)
    delivery_duration = db.Column(db.Integer, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    delivery = db.Column(db.String(100), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, nullable=True)  # 0: 대기, 1: 배송, 2: 완료, 3: 이슈

    def to_dict(self):
        return {
            'dps': self.dps,
            'eta': self.eta.isoformat() if self.eta else None,
            'sla': self.sla,
            'address': self.address,
            'zip_code': self.zip_code,
            'recipient': self.recipient,
            'contact': self.contact,
            'remark': self.remark,
            'depart_time': self.depart_time.isoformat() if self.depart_time else None,
            'arrive_time': self.arrive_time.isoformat() if self.arrive_time else None,
            'delivery_duration': self.delivery_duration,
            'department': self.department,
            'delivery': self.delivery,
            'reason': self.reason,
            'status': self.status
        }


class ReturnDelivery(db.Model):
    __tablename__ = 'return_delivery'

    # Primary Key
    dps = db.Column(db.String(50), primary_key=True)

    # Required fields
    request_date = db.Column(db.Date, nullable=False)
    package_type = db.Column(db.String(10), nullable=False)  # 소, 중, 대
    qty = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

    # Optional fields
    remark = db.Column(db.Text, nullable=True)
    dispatch_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=True)  # 대기, 회수중, 회수완료, 이슈
    reason = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'dps': self.dps,
            'request_date': self.request_date.isoformat() if self.request_date else None,
            'package_type': self.package_type,
            'qty': self.qty,
            'address': self.address,
            'recipient': self.recipient,
            'contact': self.contact,
            'remark': self.remark,
            'dispatch_date': self.dispatch_date.isoformat() if self.dispatch_date else None,
            'status': self.status,
            'reason': self.reason
        }


# Status Enums for reference
class DeliveryStatus:
    WAITING = 0
    IN_DELIVERY = 1
    COMPLETED = 2
    ISSUE = 3

    @staticmethod
    def to_string(status):
        status_map = {
            0: '대기',
            1: '배송',
            2: '완료',
            3: '이슈'
        }
        return status_map.get(status, '알 수 없음')


class ReturnStatus:
    WAITING = '대기'
    IN_PROGRESS = '회수중'
    COMPLETED = '회수완료'
    ISSUE = '이슈'

    @classmethod
    def get_all_statuses(cls):
        return [cls.WAITING, cls.IN_PROGRESS, cls.COMPLETED, cls.ISSUE]


# Helper functions for model operations
def create_delivery(data):
    delivery = Delivery(**data)
    db.session.add(delivery)
    db.session.commit()
    return delivery


def create_return(data):
    return_delivery = ReturnDelivery(**data)
    db.session.add(return_delivery)
    db.session.commit()
    return return_delivery


def update_delivery_status(dps, status, reason=None):
    delivery = Delivery.query.get(dps)
    if delivery:
        delivery.status = status
        if status == DeliveryStatus.IN_DELIVERY:
            delivery.depart_time = datetime.now()
        elif status == DeliveryStatus.COMPLETED:
            delivery.arrive_time = datetime.now()
        if reason:
            delivery.reason = reason
        db.session.commit()
        return delivery
    return None


def update_return_status(dps, status, reason=None):
    return_delivery = ReturnDelivery.query.get(dps)
    if return_delivery:
        return_delivery.status = status
        if status == ReturnStatus.IN_PROGRESS:
            return_delivery.dispatch_date = date.today()
        if reason:
            return_delivery.reason = reason
        db.session.commit()
        return return_delivery
    return None