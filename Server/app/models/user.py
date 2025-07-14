from sqlalchemy import Column, String, Enum, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .enums import UserRole
from .base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    firstName = Column(String)
    lastName = Column(String, nullable=True)
    password = Column(String)
    role = Column(Enum(UserRole))
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    lastLoginAt = Column(DateTime(timezone=True), nullable=True)
    isActive = Column(Boolean, default=True)
    isEmailVerified = Column(Boolean, default=False)
    loginCount = Column(Integer, default=0)
    
    # Relationships
    agents = relationship("Agent", back_populates="user")
    created_tasks = relationship("Task", back_populates="creator")
    submissions = relationship("Submission", back_populates="user")

    # Compatibility alias for older code/tests that expect "hashed_password" field name
    @property
    def hashed_password(self):
        return self.password

    @hashed_password.setter
    def hashed_password(self, value):
        self.password = value

    # Compatibility alias for snake_case naming in tests
    @property
    def is_active(self):
        return self.isActive

    @is_active.setter
    def is_active(self, value):
        self.isActive = value