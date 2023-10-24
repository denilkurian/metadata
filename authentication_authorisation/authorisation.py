
########## In this session finding a user who is authenticated and authenticaed persion can only create a new product 
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .private_config import SECRET_KEY,ALGORITHM
from database.models import User
from database.database import get_db
import jwt

from authentication_authorisation.auth_api.google_auth import get_user_info_from_google


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


######## this function is created for the authentication of both google auth user and normal authenticated user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

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
   

from fastapi.routing import APIRouter














