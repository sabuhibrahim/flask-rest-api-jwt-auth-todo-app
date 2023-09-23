from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, UUID4, EmailStr, validator


# ---------- User Based Schemas -------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID4

    class Config:
        orm_mode = True

    @validator("id")
    def convert_to_str(cls, v, values, **kwargs):
        return str(v) if v else v


class UserRegister(UserBase):
    password: str
    confirm_password: str

    @validator("confirm_password")
    def verify_password_match(cls, v, values, **kwargs):
        password = values.get("password")

        if v != password:
            raise ValueError("The two passwords did not match.")

        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class BlackListTokenSchema(BaseModel):
    id: UUID4
    expire: datetime


# ----------------- JWT Token Schemas ----------------
class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema


# ------------------ Todo App Content Schemas ----------------
class TaskBaseScheme(BaseModel):
    title: str
    description: Optional[str]

    class Config:
        orm_mode = True


class TaskPartialBaseScheme(BaseModel):
    title: Optional[str]
    description: Optional[str]

    @validator("title")
    def prevent_title_none(cls, v, values, **kwargs):
        assert v is not None, "This field is required"
        return v


class TaskListCreateScheme(TaskBaseScheme):
    pass


class TaskListPartialUpdateScheme(TaskPartialBaseScheme):
    order: Optional[int]

    @validator("order")
    def validate_order(cls, v, values, **kwargs):
        assert v is not None, "This field is required"
        assert int(v) >= 0, "Value must be positive number"
        return v


class UpdateOrderScheme(BaseModel):
    id: UUID4
    order: int

    @validator("order")
    def validate_order(cls, v, values, **kwargs):
        assert int(v) > 0, "Value must be greater than zero"
        return v


class TaskListScheme(TaskListCreateScheme):
    id: UUID4
    order: Optional[int]


class StepCreateScheme(BaseModel):
    title: str


class StepScheme(StepCreateScheme):
    id: UUID4


class TaskCreateScheme(TaskBaseScheme):
    reminder: Optional[datetime]
    due_date: Optional[datetime]
    tasklist_id: Optional[UUID4]
    steps: Optional[list[StepCreateScheme]]


class TaskScheme(TaskCreateScheme):
    id: UUID4
    order: Optional[int]
    steps: Optional[list[StepScheme]]


class TaskPartialUpdateSchema(TaskPartialBaseScheme):
    reminder: Optional[datetime]
    due_date: Optional[datetime]
