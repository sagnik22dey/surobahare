from sqlalchemy import Column, Integer, String, DateTime
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
