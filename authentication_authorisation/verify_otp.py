from fastapi import APIRouter, HTTPException,Depends
from authentication_authorisation.private_config import *
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
from .utils import get_password_hash
from database.models import User
from database.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()



###### function for details about email sending
def send_otp_email(recipient_email, otp):
    # SMTP_SERVER = config('SMTP_SERVER', default='')
    # SMTP_PORT = config('SMTP_PORT', default=587, cast=int)
    # SMTP_PASSWORD = config('SMTP_PASSWORD', default='')
    # SENDER_EMAIL = config('SENDER_EMAIL', default='')

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


from pydantic import BaseModel


# Assuming you have an otp_storage dictionary to store OTP data temporarily.
otp_storage = {}

class VerifyOtp(BaseModel):
    email: str
    otp: str


@router.post("/verify-otp/", tags=['authentication'])
async def verify_otp_and_create_account(verification_data: VerifyOtp, db: Session = Depends(get_db)):
    try:
        # Check if the OTP exists in storage
        stored_verification = otp_storage[verification_data.email]

        if not stored_verification:
            raise HTTPException(status_code=400, detail="OTP not found")

        if datetime.utcnow() > stored_verification['expiration']:
            raise HTTPException(status_code=400, detail="OTP has expired")

        if verification_data.otp != stored_verification['otp']:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # OTP is valid, create the user account
        user = User(
            email=verification_data.email,
            hashed_password=get_password_hash(stored_verification['hashed_password']),
            first_name=stored_verification['first_name'],
            last_name=stored_verification['last_name'],
            sex=stored_verification['sex'],
            date_of_birth=stored_verification['date_of_birth']
        )

        # Add the user to the database
        db.add(user)
        db.commit()

        # Remove the OTP from storage as it's no longer needed
        del otp_storage[verification_data.email]

        return {"message": "Account created successfully"}

    except KeyError:
        raise HTTPException(status_code=400, detail="OTP not found")

    except HTTPException as e:
        raise e











