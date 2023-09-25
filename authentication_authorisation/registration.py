from fastapi import APIRouter
from fastapi import Depends, HTTPException
from backend_services.fast_api import UserCreate
from database.models import User
from .utils import is_strong_password,get_password_hash
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.database import get_db
from pydantic import ValidationError
from datetime import datetime, timedelta
import random
import string
from .verify_otp import otp_storage,send_otp_email

router = APIRouter()


###########  registering an account
@router.post("/register/" ,tags=['authentication'])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    try:

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        if not is_strong_password(user.hashed_password):  
            raise HTTPException(status_code=400, detail="Weak password")
        
        if not user.first_name:
            raise HTTPException(status_code=400, detail="First name is required")
        
        # Generate and store OTP
        otp = ''.join(random.choice(string.digits) for _ in range(6))
        otp_expiration = datetime.utcnow() + timedelta(minutes=5)
        otp_storage[user.email] = {"otp": otp, "expiration": otp_expiration}

        # Send OTP via email
        send_otp_email(user.email, otp)


        return {"message": "Check your email id and verify otp to continue"}
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())







