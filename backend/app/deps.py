from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .config import settings
from .database import Base

# Create engine
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """FastAPI dependency that provides a database session and ensures it is closed after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT authentication dependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # retrieve user
    from .repositories.user_repository import UserRepository
    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return {"sub": str(user.id), "role": user.role, "email": user.email}
