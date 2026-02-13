from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    first_name: str
    last_name: str
    password: str
    confirm_password: str
    phone: str
    role: str = "user"  # Default role is 'user'


class ViewUser(BaseModel):
    email: EmailStr
    user_name: str
    first_name: str
    last_name: str
    phone: str


class UserLogin(BaseModel):
    user_name: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UpdateUser(BaseModel):
    user_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class DeleteUser(BaseModel):
    confirm_delete: bool = False
    user_name: str


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body_text: str | None = None
    body_html: str | None = None


class UpdatePassword(BaseModel):
    user_name: str
    old_password: str
    new_password: str
    confirm_new_password: str
