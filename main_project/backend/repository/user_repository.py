from sqlalchemy.orm import Session
from model.user_model import User


class UserRepository:
    @staticmethod
    def get_user_by_id(db: Session, user_id: str):
        return db.query(User).filter(User.user_id == user_id).first()
