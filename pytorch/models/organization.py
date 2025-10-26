"""
Organization model for managing API access and memory storage
"""
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets
import enum

from config.database import Base


class PlanType(enum.Enum):
    """Subscription plan types"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """
    Organization model for managing teams/companies using the memory service
    """
    __tablename__ = "organizations"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    
    # Plan and limits
    plan_type = Column(SQLEnum(PlanType), default=PlanType.FREE, nullable=False)
    memory_limit = Column(Integer, default=1000, nullable=False)  # Number of memories allowed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    memories = relationship("Memory", back_populates="organization", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        """Initialize organization with auto-generated API key if not provided"""
        if 'api_key' not in kwargs:
            kwargs['api_key'] = self.generate_api_key()
        super().__init__(**kwargs)

    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure random API key (max 64 chars)"""
        return f"mem_{secrets.token_urlsafe(44)}"  # 44 bytes = ~59 chars + "mem_" = ~63 chars total

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', plan='{self.plan_type.value}')>"