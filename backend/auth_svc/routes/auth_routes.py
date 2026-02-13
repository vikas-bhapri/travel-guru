from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models import auth_model
from ..schemas import auth_schema
from ..controllers import auth_controller

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=auth_schema.ViewUser,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: auth_schema.UserCreate, db: Session = Depends(get_db)):
    new_user = auth_controller.register_user(user, db)
    return new_user


@router.post("/login", response_model=auth_schema.Token, status_code=status.HTTP_200_OK)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    credentials = auth_schema.UserLogin(
        user_name=form_data.username, password=form_data.password
    )
    tokens = auth_controller.login_user(credentials, db)
    return tokens


@router.patch(
    "/update-user",
    status_code=status.HTTP_200_OK,
    response_model=auth_schema.ViewUser,
)
def update_user(
    user: auth_schema.UpdateUser,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_controller.get_current_user),
):
    if current_user["user_name"] != user.user_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )
    updated_user = auth_controller.update_user(user, db)
    return updated_user


@router.post("/delete-user", status_code=status.HTTP_202_ACCEPTED)
def delete_user(
    user: auth_schema.DeleteUser,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_controller.get_current_user),
):
    if current_user["user_name"] != user.user_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profile",
        )
    auth_controller.delete_user(user, db)
    return {"message": "User deleted successfully"}


@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(email: dict, db: Session = Depends(get_db)):
    await auth_controller.password_reset_request(email["email"], db)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def password_reset(password: dict, db: Session = Depends(get_db)):
    auth_controller.password_reset(password, db)
    return {"message": "Password reset successful"}


@router.post("/password-update", status_code=status.HTTP_200_OK)
def update_password(
    password: auth_schema.UpdatePassword,
    db: Session = Depends(get_db),
    current_user=Depends(auth_controller.get_current_user),
):
    auth_controller.update_password(password, db)
    return {"message": "Password updated successfully"}


@router.get(
    "/refresh-token", response_model=auth_schema.Token, status_code=status.HTTP_200_OK
)
def refresh_token(
    current_user=Depends(auth_controller.get_current_user),
    db: Session = Depends(get_db),
):
    new_tokens = auth_controller.refresh_token(current_user, db)
    return new_tokens

@router.get("/validate-user", status_code=status.HTTP_200_OK)
def validate_user(current_user=Depends(auth_controller.get_current_user)):
    return {"message": "User is valid", "user": current_user}
