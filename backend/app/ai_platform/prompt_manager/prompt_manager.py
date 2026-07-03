import structlog
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.ai_platform import PromptTemplate

logger = structlog.get_logger(__name__)

class PromptManager:
    """Centralized prompt management service."""

    def get_active_prompt(self, db: Session, agent_name: str, fallback_prompt: str = "") -> str:
        """Fetches the currently active prompt for an agent. Returns fallback if none exist."""
        prompt_record = db.query(PromptTemplate).filter(
            PromptTemplate.agent_name == agent_name,
            PromptTemplate.is_active == True
        ).first()

        if prompt_record:
            return prompt_record.prompt
        
        # If no active prompt exists, but a fallback is provided, let's seed it automatically
        if fallback_prompt:
            logger.info(f"Seeding fallback prompt for {agent_name}")
            self.create_new_version(db, agent_name, f"{agent_name} Initial", fallback_prompt)
            return fallback_prompt
            
        return fallback_prompt

    def create_new_version(self, db: Session, agent_name: str, title: str, prompt_text: str) -> PromptTemplate:
        """Creates a new prompt version and sets it as active. Deactivates others."""
        # Deactivate existing
        db.query(PromptTemplate).filter(PromptTemplate.agent_name == agent_name).update({"is_active": False})
        
        # Determine next version
        latest = db.query(PromptTemplate).filter(PromptTemplate.agent_name == agent_name).order_by(PromptTemplate.version.desc()).first()
        next_version = (latest.version + 1) if latest else 1
        
        new_prompt = PromptTemplate(
            agent_name=agent_name,
            version=next_version,
            title=title,
            prompt=prompt_text,
            is_active=True
        )
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
        return new_prompt
        
    def rollback_version(self, db: Session, agent_name: str, version: int) -> bool:
        """Rolls back an agent's active prompt to a specific version."""
        target = db.query(PromptTemplate).filter(PromptTemplate.agent_name == agent_name, PromptTemplate.version == version).first()
        if not target:
            return False
            
        db.query(PromptTemplate).filter(PromptTemplate.agent_name == agent_name).update({"is_active": False})
        target.is_active = True
        db.commit()
        return True

    def get_all_prompts(self, db: Session) -> List[PromptTemplate]:
        return db.query(PromptTemplate).order_by(PromptTemplate.agent_name, PromptTemplate.version.desc()).all()

prompt_manager = PromptManager()
