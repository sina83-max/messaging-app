from typing import Optional

from pydantic import BaseModel, EmailStr, root_validator, model_validator


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

    # Return the ORM object directly
    class Config:
        from_attributes = True


class UserUpdateUsername(BaseModel):
    username: str
