from fastapi import APIRouter, Depends

from schemas import UserResponse
from models import User
from auth.auth_handler import get_current_active_user

user_router= APIRouter()

@user_router.get('/users/me', response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
  return current_user