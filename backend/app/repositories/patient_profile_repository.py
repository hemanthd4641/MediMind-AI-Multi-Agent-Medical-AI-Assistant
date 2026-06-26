from sqlalchemy.orm import Session
from ..models.patient_profile import PatientProfile
from typing import Optional

class PatientProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> Optional[PatientProfile]:
        return self.db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()

    def create(self, user_id: str, **kwargs) -> PatientProfile:
        profile = PatientProfile(user_id=user_id, **kwargs)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: PatientProfile, **kwargs) -> PatientProfile:
        for key, value in kwargs.items():
            setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile
