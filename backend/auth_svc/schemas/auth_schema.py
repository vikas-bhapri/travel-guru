from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    first_name: str
    last_name: str
    password: str
    confirm_password: str
    phone: str


class ViewUser(BaseModel):
    email: EmailStr
    user_name: str
    first_name: str
    last_name: str
    phone: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
