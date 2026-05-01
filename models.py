from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_name = Column(String, nullable=False)
    child_name = Column(String, nullable=False)
    child_age = Column(Integer, nullable=False)
    mobile = Column(String, nullable=False)
    location = Column(String, nullable=False)
    program_interest = Column(String, nullable=False)
    heard_from = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SiteContent(Base):
    __tablename__ = "site_content"

    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    recovery_code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    session_token = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
