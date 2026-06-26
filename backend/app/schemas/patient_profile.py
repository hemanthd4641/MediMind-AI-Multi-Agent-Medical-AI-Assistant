from pydantic import BaseModel, Field
from typing import Optional

class PatientProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    medical_record_number: Optional[str] = None

    class Config:
        orm_mode = True
