from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from schemas import UserResponse, UserCreate, Token
from database import get_db
from models import User

from auth.auth_handler import get_user, get_password_hash, authenticate_user,ACCESS_TOKEN_EXPIRES_MINUTES, create_access_token

auth_router= APIRouter()

@auth_router.post('/register', response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
  db_user= get_user(db, user.username)
  if db_user:
    return HTTPException(status_code=400, detail='username already registered')

  hashed_password= get_password_hash(user.password)
  db_user= User(
    username=user.username,
    email=user.email,
    hashed_password=hashed_password

  )

  db.add(db_user)
  db.commit()
  db.refresh(db_user)

  return db_user

@auth_router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db))-> Token:
  user= authenticate_user(db, form_data.username, form_data.password)
  if not user:
    raise HTTPException(status_code=401, detail='Incorrect username or password', headers={'WWW-Authenticate': 'bearer'})
  
  access_token_expires= timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
  access_token= create_access_token(
     data={'sub': user.username}, 
    expires_delta=access_token_expires
  )

  return Token(access_token=access_token, token_type='bearer')