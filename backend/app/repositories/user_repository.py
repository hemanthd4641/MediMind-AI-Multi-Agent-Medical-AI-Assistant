from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from typing import Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, full_name: str, email: str, password_hash: str, phone: Optional[str] = None, role: str = UserRole.PATIENT.value) -> User:
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            role=role,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, new_hash: str) -> User:
        user.password_hash = new_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_verified(self, user: User, verified: bool = True) -> User:
        user.is_verified = verified
        self.db.commit()
        self.db.refresh(user)
        return user
