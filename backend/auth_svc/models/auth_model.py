from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class Users(Base):
    __tablename__ = "users"

    user_name = Column(String, primary_key=True, index=True, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(
        TIMESTAMP,
        default=datetime.utcnow(),
        onupdate=datetime.utcnow(),
    )
    user_sessions = relationship("UserSessions", back_populates="user")


class UserSessions(Base):
    __tablename__ = "user_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String, ForeignKey("users.user_name"), nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)

    user = relationship("Users", back_populates="user_sessions")
