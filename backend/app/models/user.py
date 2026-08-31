import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", backref="users")

    created_at = Column(DateTime, default=datetime.utcnow)