from typing import Optional

from fastapi import UploadFile, File
from pydantic import BaseModel, EmailStr, root_validator, model_validator, constr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str



class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @model_validator(mode="after")
    def check_username_email(self):
        if not self.username and not self.email:
            raise ValueError("Either Username or Email is required.")

        return self


class UserResponse(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None

    # Return the ORM object directly
    class Config:
        from_attributes = True


class UserUpdateProfile(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None

    @model_validator(mode="after")
    def check_username_avatar_url(self):
        if not self.username and not self.avatar_url:
            raise ValueError("Either Username or Avatar URL is required.")
        return self


class UserUpdatePassword(BaseModel):
    old_password: constr(min_length=6)
    new_password: constr(min_length=6)
    repeat_new_password: constr(min_length=6)
