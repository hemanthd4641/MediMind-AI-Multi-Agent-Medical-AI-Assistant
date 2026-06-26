import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import config
from ..models.user import User, UserRole
from ..models.refresh_token import RefreshToken
from ..repositories.user_repository import UserRepository
from ..repositories.refresh_token_repository import RefreshTokenRepository
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
        self.settings = config.settings

    # ---------- Password handling ----------
    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # ---------- Token generation ----------
    def _create_access_token(self, user_id: uuid.UUID, role: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "role": role, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.settings.JWT_SECRET_KEY, algorithm=self.settings.JWT_ALGORITHM)
        return encoded_jwt

    def _create_refresh_token(self, user_id: uuid.UUID) -> RefreshToken:
        token_str = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return self.refresh_repo.create(user_id=user_id, token=token_str, expires_at=expires_at)

    # ---------- Public API ----------
    def register_user(self, full_name: str, email: str, password: str, phone: Optional[str] = None, role: str = UserRole.PATIENT.value) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed = self._hash_password(password)
        user = self.user_repo.create(full_name=full_name, email=email, password_hash=hashed, phone=phone, role=role)
        return user

    def authenticate_user(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not self._verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = self._create_access_token(user.id, user.role)
        refresh_obj = self._create_refresh_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_obj.token,
            "token_type": "bearer",
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        token_obj = self.refresh_repo.get_by_token(refresh_token)
        if not token_obj or token_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        user = self.user_repo.get(token_obj.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        new_access = self._create_access_token(user.id, user.role)
        return {"access_token": new_access, "token_type": "bearer"}

    def revoke_refresh_token(self, refresh_token: str) -> None:
        self.refresh_repo.revoke(refresh_token)
