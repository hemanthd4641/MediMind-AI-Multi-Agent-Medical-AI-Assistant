from fastapi import APIRouter, Depends, HTTPException, status, Body

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .. import deps
from ..services.auth_service import AuthService
from ..schemas.token import TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str | None = None
    role: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(deps.get_db)):
    service = AuthService(db)
    user = service.register_user(
        full_name=request.full_name,
        email=request.email,
        password=request.password,
        phone=request.phone,
        role=request.role or "patient",
    )
    tokens = service.authenticate_user(request.email, request.password)
    return TokenResponse(**tokens)

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(deps.get_db)):
    service = AuthService(db)
    tokens = service.authenticate_user(request.email, request.password)
    return TokenResponse(**tokens)

@router.post("/refresh")
def refresh(refresh_token: str = Body(...), db: Session = Depends(deps.get_db)):
    # The refresh token is expected in the request body as plain string
    service = AuthService(db)
    return service.refresh_access_token(refresh_token)

@router.post("/logout")
def logout(refresh_token: str = Body(...), db: Session = Depends(deps.get_db)):
    service = AuthService(db)
    service.revoke_refresh_token(refresh_token)
    return {"detail": "Logged out"}


@router.get("/me")
def get_me(current_user: dict = Depends(deps.get_current_user)):
    return current_user
