from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
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
