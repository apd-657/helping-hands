# models.py
# These are the database TABLE definitions
# Each class = one table in SQLite

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ─────────────────────────────────────────────
# USERS TABLE
# Stores both Elders and Volunteers
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    age           = Column(Integer, nullable=True)
    role          = Column(String(20), nullable=False)   # "elder" or "volunteer"
    contact       = Column(String(20), nullable=True)   # phone number
    location      = Column(String(200), nullable=True)  # city / area
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (link to requests table)
    requests_made     = relationship("HelpRequest", back_populates="elder",
                                     foreign_keys="HelpRequest.elder_id")
    requests_accepted = relationship("HelpRequest", back_populates="volunteer",
                                     foreign_keys="HelpRequest.volunteer_id")


# ─────────────────────────────────────────────
# HELP REQUESTS TABLE
# Stores requests created by Elders
# ─────────────────────────────────────────────
class HelpRequest(Base):
    __tablename__ = "requests"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(200), nullable=False)         # e.g. "Need grocery shopping"
    description  = Column(Text, nullable=False)                # detailed explanation
    category     = Column(String(50), nullable=False)          # grocery/hospital/medicine/other
    location     = Column(String(200), nullable=False)         # where help is needed
    status       = Column(String(20), default="pending")       # pending/accepted/completed
    elder_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null until accepted
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    elder     = relationship("User", back_populates="requests_made",
                             foreign_keys=[elder_id])
    volunteer = relationship("User", back_populates="requests_accepted",
                             foreign_keys=[volunteer_id])


# ─────────────────────────────────────────────
# MESSAGES TABLE (Basic Chat Feature)
# ─────────────────────────────────────────────
class Message(Base):
    __tablename__ = "messages"

    id         = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    sender_id  = Column(Integer, ForeignKey("users.id"), nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    request = relationship("HelpRequest")
    sender  = relationship("User")
