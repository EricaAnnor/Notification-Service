from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON,String
from datetime import datetime
from pydantic import EmailStr, model_validator
from fastapi import HTTPException, status
import uuid
from typing import Any, Dict, Optional
import enum


class Channel(str, enum.Enum):
    sms = "sms"
    push = "push"
    email = "email"


class State(str, enum.Enum):
    sent = "sent"
    failed = "failed"
    in_progress = "in_progress"


class UserCreate(SQLModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    @model_validator(mode='after')
    def check_email_or_number(cls, values):
        if not values.email and not values.phone_number:
            raise HTTPException(
                detail="Should contain either phone number or email",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return values


class User(UserCreate, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory =datetime.now)


class UserResponse(User):
    class Config:
        orm_mode = True


class NotificationSettings(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    channel: Channel
    opt_in: bool = Field(default=True)

class EmailCreate(SQLModel):
    sender:EmailStr
    receiver:EmailStr
    title:str
    content:str

class SmsCreate(SQLModel):
    receiver:str
    message:str


class EmailNotificationLog(EmailCreate, table=True):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    retries_count: int = Field(default=0)
    state: State = Field(default="in_progress")
   

class SmsNotificationLog(SmsCreate, table=True):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    retries_count: int = Field(default=0)
    state: State = Field(default="in_progress")
    


class NotificationResponse(SQLModel):
    message:str
    event_id:uuid.UUID

