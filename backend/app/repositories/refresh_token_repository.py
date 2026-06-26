from sqlalchemy.orm import Session
from ..models.refresh_token import RefreshToken
from datetime import datetime

class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id, token: str, expires_at: datetime) -> RefreshToken:
        refresh = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(refresh)
        self.db.commit()
        self.db.refresh(refresh)
        return refresh

    def get_by_token(self, token: str) -> RefreshToken | None:
        return self.db.query(RefreshToken).filter(RefreshToken.token == token).first()

    def revoke(self, token: str) -> None:
        rt = self.get_by_token(token)
        if rt:
            self.db.delete(rt)
            self.db.commit()
