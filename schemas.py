from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EnrollmentCreate(BaseModel):
    parent_name: str
    child_name: str
    child_age: int
    mobile: str
    location: str
    program_interest: str
    heard_from: Optional[str] = None


class EnrollmentRead(EnrollmentCreate):
    id: int
    created_at: datetime
