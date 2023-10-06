from fastapi import Depends, HTTPException, status, FastAPI, Query, Response,Request
from fastapi.routing import APIRouter
from authentication_authorisation.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from authlib.integrations.starlette_client import OAuth
from fastapi.security.oauth2 import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.responses import JSONResponse
from fastapi.responses import RedirectResponse
from database.models import *
from database.database import SessionLocal
import requests
from sqlalchemy.orm import Session



router = APIRouter()



@router.get("/auth/google")
def google_oauth_login():
    # Construct the Google OAuth2 URL with your client ID and redirect URI
    google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
    client_id = "776635407081-a1dhm9214g8cqatujv7rsbcbge5mff8b.apps.googleusercontent.com"
    redirect_uri = "http://127.0.0.1:8000/auth/google/callback"
    scope = "openid profile email"  # Define required scopes
    return RedirectResponse(f"{google_oauth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code")


GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"
GOOGLE_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"

def exchange_code_for_access_token(code: str) -> dict:
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    return response.json()


@router.get("/auth/google/callback")
async def google_oauth_callback(
    request: Request,
    code: str = Query(...),
    db: Session = Depends(lambda r: SessionLocal())
):
    # Exchange the authorization code for an access token
    google_auth_data = exchange_code_for_access_token(code)
    
    # Fetch user data from Google API
    google_user_data = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", 
        headers={"Authorization": f"Bearer {google_auth_data['access_token']}"}
    ).json()
    
    # Check if the user already exists in the database
    existing_google_user = db.query(GoogleAuthUser).filter_by(google_id=google_user_data['id']).first()
    
    if existing_google_user:
        # User already exists, log them in
        user = existing_google_user.user
    else:
        # Create a new user in the database
        user = User(
            first_name=google_user_data['given_name'],
            last_name=google_user_data['family_name'],
            email=google_user_data['email'],
        )
        db.add(user)
        db.commit()
        
        # Create a GoogleAuthUser entry to link the user with their Google account
        google_auth_user = GoogleAuthUser(google_id=google_user_data['id'], user=user)
        db.add(google_auth_user)
        db.commit()
    
    # Implement your own user authentication logic here if needed
    # For simplicity, we're just returning a message
    return {"message": "Successfully logged in with Google"}





