from typing import Optional
from sqlalchemy.orm import Session
from ..models.patient_profile import PatientProfile
from ..repositories.patient_profile_repository import PatientProfileRepository

class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PatientProfileRepository(db)

    def get_profile(self, user_id) -> Optional[PatientProfile]:
        return self.repo.get_by_user_id(user_id)

    def update_profile(self, user_id, **kwargs) -> PatientProfile:
        profile = self.repo.get_by_user_id(user_id)
        if not profile:
            # Create if not exists
            profile = self.repo.create(user_id=user_id, **kwargs)
        else:
            for key, value in kwargs.items():
                setattr(profile, key, value)
            self.db.commit()
            self.db.refresh(profile)
        return profile
