from fastapi import Depends, HTTPException, status, FastAPI, Query, Response,Request
from fastapi.routing import APIRouter
from authentication_authorisation.private_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
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


@router.get("/auth/google", tags =["google_auth"])
def google_oauth_login():
    # Construct the Google OAuth2 URL with your client ID and redirect URI
    google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
    client_id = GOOGLE_CLIENT_ID
    redirect_uri = "http://127.0.0.1:8000/auth/google/callback"
    scope = "openid profile email"  # Define required scopes
    auth_url = f"{google_oauth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code" 
    return RedirectResponse(url=auth_url, status_code=302)



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

    if response.status_code == 200:
        access_token_data = response.json()
        access_token = access_token_data.get("access_token")
        return access_token_data
    else:
        error_response = response.json()
        return error_response



import urllib.parse



@router.get("/auth/google/callback", tags=["google_auth"])
async def google_oauth_callback(request: Request, code: str):
    # URL-decode the authorization code
    authorization_code = urllib.parse.unquote(code)

    # Exchange the authorization code for an access token
    access_token_data = exchange_code_for_access_token(authorization_code)

    if "access_token" in access_token_data:
        # You have obtained the access token, you can use it for authentication
        access_token = access_token_data["access_token"]
        # You can return the access token or perform further actions here
        return JSONResponse(content={"access_token": access_token}, status_code=200)
    else:
        # Handle the case where the access token is not obtained
        error_message = access_token_data.get("error_description", "Access token not obtained.")
        return JSONResponse(content={"error": error_message}, status_code=400)












