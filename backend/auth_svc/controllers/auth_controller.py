from ..models import auth_model
from ..schemas import auth_schema
from bcrypt import hashpw, gensalt
from fastapi import status, HTTPException
from sqlalchemy.orm import Session
import email_validator


def hash_password(password: str):
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


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

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)


def register_user(user: auth_schema.UserCreate, db: Session):
    # Check if the user already exists
    existing_user = (
        db.query(auth_model.Users).filter(auth_model.Users.email == user.email).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    validate_registration_data(user)

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
