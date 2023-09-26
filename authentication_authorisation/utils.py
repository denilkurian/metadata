
############ in this session generation of token , validity , secret key etc defined

from database.models import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from decouple import AutoConfig

config = AutoConfig()

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_strong_password(password: str) -> bool:
    # password complexity rules here
    min_length = 8
    has_uppercase = any(char.isupper() for char in password)
    has_lowercase = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special_char = any(char in "!@#$%^&*(),.?\":{}|<>" for char in password)

    return (
        len(password) >= min_length and
        has_uppercase and
        has_lowercase and
        has_digit and
        has_special_char
    )

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


 









