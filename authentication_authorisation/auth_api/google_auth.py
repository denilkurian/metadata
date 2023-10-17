from fastapi import Depends, HTTPException, status, FastAPI, Query, Response,Request
from fastapi.routing import APIRouter
from authentication_authorisation.private_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from authlib.integrations.starlette_client import OAuth
from fastapi.security.oauth2 import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.responses import JSONResponse
from fastapi.responses import RedirectResponse
from database.models import *
import requests


router = APIRouter()

######### api to redirect to google auth page
@router.get("/auth/google", tags=["google_auth"])
def google_oauth_login():
    # Construct the Google OAuth2 URL with your client ID and redirect URI
    google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
    client_id = GOOGLE_CLIENT_ID
    redirect_uri = "http://127.0.0.1:8000/auth/google/callback"
    scope = "openid profile email"  # Define required scopes
    auth_url = f"{google_oauth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code" 
    return auth_url



GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"
GOOGLE_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"


######## getting token from google
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
        return access_token_data
    else:
        error_response = response.json()
        return error_response




########## fetching user info from google account , here we fetch email id
import requests

def get_user_info_from_google(access_token):
    # Define the Google API endpoint for fetching user info
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    # Set up the headers with the access token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Make a GET request to the Google API
    response = requests.get(user_info_url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        error_message = response.json().get("error_description", "Failed to fetch user info from Google")
        raise Exception(error_message)





########## callback api which give access token after authentication and stores user email in same database.
import urllib
from database.database import SessionLocal


@router.get("/auth/google/callback", tags=["google_auth"])
async def google_oauth_callback(request: Request, code: str):
    # URL-decode the authorization code
    authorization_code = urllib.parse.unquote(code)

    # Exchange the authorization code for an access token
    access_token_data = exchange_code_for_access_token(authorization_code)

    if "access_token" in access_token_data:
        access_token = access_token_data["access_token"]
        # You can use the access token for authentication or further actions

        # Fetch the user's email from Google (you may need to make an API request)
        google_user_info = get_user_info_from_google(access_token)

        if "email" in google_user_info:
            user_email = google_user_info["email"]
            # Save the email in your User model or perform any other actions
            user = User(email=user_email)
            db = SessionLocal()
            db.add(user)
            db.commit()
            db.close()

            # Return the email and access token
            return JSONResponse(content={"email": user_email, "access_token": access_token}, status_code=200)
        else:
            return JSONResponse(content={"error": "Email not obtained from Google"}, status_code=400)
    else:
        error_message = access_token_data.get("error_description", "Access token not obtained.")
        return JSONResponse(content={"error": error_message}, status_code=400)
    










