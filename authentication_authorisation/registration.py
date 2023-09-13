from fastapi import APIRouter
from fastapi import Depends, HTTPException
from backend_services.fast_api import UserCreate
from database.models import User
from .utils import is_strong_password,get_password_hash
from sqlalchemy.orm import Session
from database.database import get_db


router = APIRouter()


###########  registering an account
@router.post("/register/" ,tags=['authentication'])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    if not is_strong_password(user.hashed_password):  
        raise HTTPException(status_code=400, detail="Weak password")

    hashed_password = get_password_hash(user.hashed_password)  

    new_user = User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}












