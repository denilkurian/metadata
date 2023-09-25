from fastapi import APIRouter, HTTPException, Query,Depends,Body
from decouple import config
from email.mime.text import MIMEText
import smtplib
from datetime import datetime, timedelta
from .utils import get_password_hash
from database.models import User
from database.database import get_db
from sqlalchemy.orm import Session
from backend_services.fast_api import UserCreate

router = APIRouter()

otp_storage = {}

###### function for details about email sending
def send_otp_email(recipient_email, otp):
    SMTP_SERVER = config('SMTP_SERVER', default='')
    SMTP_PORT = config('SMTP_PORT', default=587, cast=int)
    SMTP_PASSWORD = config('SMTP_PASSWORD', default='')
    SENDER_EMAIL = config('SENDER_EMAIL', default='')

    subject = "OTP Verification"
    message = f"Your OTP: {otp}"

    # Create an email message
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Use TLS for security

        # Login to the sender's email account
        server.login(SENDER_EMAIL,SMTP_PASSWORD)

        # Send the email
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        # Disconnect from the SMTP server
        server.quit()

        print(f"OTP sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Email sending failed: {e}")


########## api for otp verification 
@router.post("/verify-otp-and-create-account/", tags=['authentication'])
async def verify_otp_and_create_account(email: str = Query(..., description="User's email address"), otp: str = Query(..., description="OTP received via email"), db: Session = Depends(get_db), user: UserCreate = Body(...)):


    stored_otp_info = otp_storage.get(email)

    if not stored_otp_info:
        raise HTTPException(status_code=400, detail="Invalid email or OTP")

    stored_otp = stored_otp_info.get("otp")
    expiration = stored_otp_info.get("expiration")

    if otp != stored_otp or datetime.utcnow() > expiration:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP has expired")

    # Create the user account in the database
    hashed_password = get_password_hash(user.hashed_password)
    new_user = User(first_name=user.first_name, last_name=user.last_name, sex=user.sex, date_of_birth=user.date_of_birth, hashed_password=hashed_password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Remove the verified OTP from storage (optional)
    del otp_storage[email]

    return {"message": "User account created successfully"}













