# schemas.py
# Pydantic schemas = data shapes for incoming requests and outgoing responses
# FastAPI uses these to VALIDATE data automatically

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────────
class UserRegister(BaseModel):
    name:     str
    email:    EmailStr
    password: str
    age:      Optional[int] = None
    role:     str           # "elder" or "volunteer"
    contact:  Optional[str] = None
    location: Optional[str] = None

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type:   str
    user_id:      int
    name:         str
    role:         str

class UserOut(BaseModel):
    id:       int
    name:     str
    email:    str
    age:      Optional[int]
    role:     str
    contact:  Optional[str]
    location: Optional[str]

    class Config:
        from_attributes = True   # allows reading from SQLAlchemy objects


# ─────────────────────────────────────────────
# HELP REQUEST SCHEMAS
# ─────────────────────────────────────────────
class RequestCreate(BaseModel):
    title:       str
    description: str
    category:    str   # grocery / hospital / medicine / other
    location:    str

class RequestOut(BaseModel):
    id:           int
    title:        str
    description:  str
    category:     str
    location:     str
    status:       str
    elder_id:     int
    volunteer_id: Optional[int]
    created_at:   datetime
    elder:        Optional[UserOut]
    volunteer:    Optional[UserOut]

    class Config:
        from_attributes = True

class RequestStatusUpdate(BaseModel):
    status: str   # "accepted" or "completed"


# ─────────────────────────────────────────────
# MESSAGE SCHEMAS
# ─────────────────────────────────────────────
class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id:         int
    request_id: int
    sender_id:  int
    content:    str
    created_at: datetime
    sender:     Optional[UserOut]

    class Config:
        from_attributes = True
