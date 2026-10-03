# serializers/user.py — request/response schemas for users and auth.

from pydantic import BaseModel, ConfigDict


class UserRegistrationSchema(BaseModel):
    username: str
    email: str
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    role: str = "user"

    model_config = ConfigDict(from_attributes=True)


class UserTokenSchema(BaseModel):
    token: str
    message: str