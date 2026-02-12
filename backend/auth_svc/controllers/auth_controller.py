from ..models import auth_model
from ..schemas import auth_schema
from ..database.database import get_db
from .password_reset import send_email
from bcrypt import hashpw, gensalt, checkpw
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import email_validator
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import time
import os
from dotenv import load_dotenv
import hashlib, secrets

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET", "kasldjflasdjflaksjdflkasjf")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def hash_password(password: str):
    return hashpw(password.encode("utf-8"), gensalt(rounds=10)).decode("utf-8")


def validate_registration_data(user: auth_schema.UserCreate):
    errors = {}
    if user.password != user.confirm_password:
        errors["password"] = "Passwords do not match"

    if len(user.password) < 8:
        errors["password"] = "Password must be at least 8 characters long"

    try:
        email_validator.validate_email(user.email, check_deliverability=False)
    except email_validator.EmailNotValidError as e:
        errors["email"] = str(e)

    if len(user.phone) != 10 or not user.phone.isdigit():
        errors["phone"] = "Phone number must be 10 digits long"

    if user.role == "admin":
        errors["role"] = "Cannot register as admin"

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)


def register_user(user: auth_schema.UserCreate, db: Session):
    # Validate data first before hitting the database
    validate_registration_data(user)

    # Check if the user already exists
    existing_user = (
        db.query(auth_model.Users).filter(auth_model.Users.email == user.email).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash the password
    password_hash = hash_password(user.password)

    # Create a new user instance
    new_user = auth_model.Users(
        email=user.email,
        user_name=user.user_name,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=password_hash,
        phone=user.phone,
    )

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def generate_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def login_user(credentials: auth_schema.UserLogin, db: Session):
    user = (
        db.query(auth_model.Users)
        .filter(auth_model.Users.user_name == credentials.user_name)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not checkpw(
        credentials.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    data = {"sub": user.user_name, "role": user.role}

    access_token = generate_token(data, expires_delta=timedelta(minutes=15))
    refresh_token = generate_token(data, expires_delta=timedelta(days=7))

    existing_sessions = (
        db.query(auth_model.UserSessions)
        .filter(auth_model.UserSessions.user_name == user.user_name)
        .all()
    )
    for session in existing_sessions:
        db.delete(session)

    new_session = auth_model.UserSessions(
        user_name=user.user_name,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {"access_token": access_token, "refresh_token": refresh_token}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_name = payload.get("sub")
        role = payload.get("role")
        if user_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return {"user_name": user_name, "role": role}


def update_user(user: auth_schema.UpdateUser, db: Session):
    existing_user = (
        db.query(auth_model.Users)
        .filter(auth_model.Users.user_name == user.user_name)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    for field, value in user.model_dump(exclude_unset=True).items():
        if field != "user_name":  # Don't update the primary key
            setattr(existing_user, field, value)

    db.commit()
    db.refresh(existing_user)
    return existing_user


def delete_user(user: auth_schema.DeleteUser, db: Session):
    if not user.confirm_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please confirm deletion"
        )

    existing_user = (
        db.query(auth_model.Users)
        .filter(auth_model.Users.user_name == user.user_name)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Delete associated user sessions first
    db.query(auth_model.UserSessions).filter(
        auth_model.UserSessions.user_name == user.user_name
    ).delete()

    # Now delete the user
    db.delete(existing_user)
    db.commit()

    return {"message": "User deleted successfully"}


async def password_reset_request(email: str, db: Session) -> dict:
    user = db.query(auth_model.Users).filter(auth_model.Users.email == email).first()
    if not user:
        return {}  # Don't reveal if the email exists

    reset_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

    new_reset_token = auth_model.ResetPasswordTokens(
        user_name=user.user_name,
        hashed_token=hashed_token,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    db.add(new_reset_token)
    db.commit()
    db.refresh(new_reset_token)

    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    email_request = auth_schema.EmailRequest(
        to=email,
        subject="Password Reset Request",
        body_text=f"Click the link to reset your password: {reset_link}",
        body_html=f"<p>Click the link to reset your password: <a href='{reset_link}'>Reset Password</a></p>",
    )

    await send_email(email_request)

    return {"message": "Password reset email sent"}


def password_reset(password_data: dict[str, str], db: Session):
    token = password_data.get("token")
    new_password = password_data.get("new_password")
    confirm_password = password_data.get("confirm_password")

    if not token or not new_password or not confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields"
        )

    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    hashed_token = hashlib.sha256(token.encode()).hexdigest()

    reset_token_entry = (
        db.query(auth_model.ResetPasswordTokens)
        .filter(auth_model.ResetPasswordTokens.hashed_token == hashed_token)
        .first()
    )
    if not reset_token_entry or reset_token_entry.used is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    # Make expires_at timezone-aware if it's naive
    expires_at = reset_token_entry.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired"
        )

    hashed_password = hash_password(new_password)

    user = (
        db.query(auth_model.Users)
        .filter(auth_model.Users.user_name == reset_token_entry.user_name)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.password_hash = hashed_password
    reset_token_entry.used = True

    db.commit()

    return {"message": "Password reset successful"}


def update_password(password_data: auth_schema.UpdatePassword, db: Session):
    user = (
        db.query(auth_model.Users)
        .filter(auth_model.Users.user_name == password_data.user_name)
        .first()
    )

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, {"message": "User not found"})

    if not checkpw(
        password_data.old_password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, {"message": "Old password is incorrect"}
        )

    if password_data.new_password != password_data.confirm_new_password:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, {"message": "New passwords do not match"}
        )

    if len(password_data.new_password) < 8:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"message": "Password must be at least 8 characters long"},
        )

    user.password_hash = hash_password(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
