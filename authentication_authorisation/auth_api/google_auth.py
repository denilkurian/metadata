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
async def google_oauth_callback(request: Request):
    authorization_code = request.query_params.get("code")
    print("Authorization Code:", authorization_code)








