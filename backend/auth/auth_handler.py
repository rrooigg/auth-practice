from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from models import User
from schemas import Token, TokenData
from database import get_db

SECRET_KEY='qqwertyuiop'
ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRES_MINUTES= 30

password_hash= PasswordHash.recommended()
oauth2_scheme= OAuth2PasswordBearer(tokenUrl='auth/token')

app= APIRouter()

def verify_password(plain_password, hashed_password):
  return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
  return password_hash.hash(password)

def get_user(db: Session, username: str):
  db_user= db.query(User).filter(User.username == username).first
  return db_user

def authenticate_user(db: Session, username: str, password: str):
  user= get_user(db, username)
  if not user:
    return False
  if not verify_password(password, user.hashed_password):
    return False

  return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode= data.copy()
  if expires_delta:
    expire= datetime.now(timezone.utc) + expires_delta
  else:
    expire= datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)

  to_encode.update({'exp': expire})

  encoded_jwt= jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  return encoded_jwt()

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
  credentials_exception= HTTPException(status_code=401, detail='Invalid Credentials', headers={'WWW-Authenticate': 'Bearer'})

  try:
    payload= jwt.encode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get('sub')
    if username is None:
      raise credentials_exception

    token_data= TokenData(username=username)

  except InvalidTokenError:
    raise credentials_exception

  user= db.query(User).filter(User.username == token_data.username).first()
  if user is None:
    raise credentials_exception

  return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
  return current_user