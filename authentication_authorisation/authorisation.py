
########## In this session finding a user who is authenticated and authenticaed persion can only create a new product 
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from authentication_authorisation.private_config import SECRET_KEY,ALGORITHM
from database.models import User
from database.database import get_db
import jwt

from authentication_authorisation.auth_api.google_auth import get_user_info_from_google,exchange_code_for_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to validate the token as a Google token
    try:
        google_user_info = get_user_info_from_google(token)
        if google_user_info is not None:
            email = google_user_info.get("email")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return user
    except Exception:
        pass

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(User).filter(User.email == username).first()
        if user is not None:
            return user
    except jwt.PyJWTError:
        raise credentials_exception

    raise credentials_exception
   













