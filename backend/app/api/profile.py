from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .. import deps
from ..services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])

class PatientProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    medical_record_number: str | None = None

    class Config:
        orm_mode = True

@router.get("/me", response_model=PatientProfileResponse)
def get_my_profile(db: Session = Depends(deps.get_db), current_user: dict = Depends(deps.get_current_user)):
    service = ProfileService(db)
    profile = service.get_profile(current_user["sub"])  # user_id stored in JWT "sub"
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile

@router.put("/me", response_model=PatientProfileResponse)
def update_my_profile(payload: PatientProfileResponse, db: Session = Depends(deps.get_db), current_user: dict = Depends(deps.get_current_user)):
    service = ProfileService(db)
    updated = service.update_profile(current_user["sub"], **payload.dict(exclude={"id", "user_id"}))
    return updated
