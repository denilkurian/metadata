from fastapi import APIRouter,Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import  Depends,HTTPException
from database.models import User
from database.database import get_db
from authentication_authorisation.utils import verify_password
from .utils import get_password_hash,create_access_token


router = APIRouter()


#################### In this session login a user or authentication and generate the access token for the user
@router.post("/token", tags=['authentication'])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Get the user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Generate and return an access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}




