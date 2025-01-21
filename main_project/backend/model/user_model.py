from sqlalchemy import Column, String, Enum
from config.main_config import Base


class User(Base):
    __tablename__ = "user"
    user_id = Column(String(45), primary_key=True)
    user_password = Column(String(255), nullable=False)
    authority = Column(Enum("manager", "staff"), nullable=False)
