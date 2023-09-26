from fastapi import APIRouter
from fastapi import Depends, HTTPException
from backend_services.fast_api import UserCreate
from database.models import User
from .utils import is_strong_password
from sqlalchemy.orm import Session
from database.database import get_db
from pydantic import ValidationError
from datetime import datetime, timedelta
import random
import string
from .verify_otp import otp_storage,send_otp_email


router = APIRouter()



@router.post("/register/", tags=['authentication'])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    try:
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        if not is_strong_password(user.hashed_password):  
            raise HTTPException(status_code=400, detail="Weak password")
        
        if not user.first_name:
            raise HTTPException(status_code=400, detail="First name is required")
        
        # Generate and store OTP along with account creation details
        otp = ''.join(random.choice(string.digits) for _ in range(6))
        otp_expiration = datetime.utcnow() + timedelta(minutes=5)
        otp_storage[user.email] = {
            "otp": otp,
            "expiration": otp_expiration,
            "hashed_password": user.hashed_password,  # Store the hashed_password
            "first_name": user.first_name,  # Store other account creation details
            "last_name": user.last_name,
            "sex": user.sex,
            "date_of_birth": user.date_of_birth
        }
        
        print(otp_storage)
        # Send OTP via email
        send_otp_email(user.email, otp)

        return {"message": "Check your email id and verify OTP to continue", "email": user.email}
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())









