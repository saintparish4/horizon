"""
Memory model for storing contextual information with vector embeddings
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, ARRAY, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime

from config.database import Base


class Memory(Base):
    """
    Memory model for storing user/session context with semantic search capabilities
    """
    __tablename__ = "memories"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # OpenAI embeddings are 1536 dimensions
    
    # Context information
    context_type = Column(String(50), nullable=True, index=True)  # e.g., "conversation", "document", "user_profile"
    user_id = Column(String(255), nullable=True, index=True)  # External user identifier
    session_id = Column(String(255), nullable=True, index=True)  # Session/conversation identifier
    
    # Metadata and tags
    metadata = Column(JSON, default=dict, nullable=True)  # Flexible JSON metadata
    tags = Column(ARRAY(String), default=list, nullable=True)  # Array of tags for categorization
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Track last access for analytics
    
    # Relationships
    organization = relationship("Organization", back_populates="memories")

    def __repr__(self):
        return f"<Memory(id={self.id}, org_id={self.org_id}, user_id='{self.user_id}', type='{self.context_type}')>"


# Additional indexes for performance optimization
Index('ix_memories_org_user', Memory.org_id, Memory.user_id)
Index('ix_memories_org_session', Memory.org_id, Memory.session_id)
Index('ix_memories_org_context_type', Memory.org_id, Memory.context_type)
Index('ix_memories_created_at_desc', Memory.created_at.desc())