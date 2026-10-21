from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth_router
from routers.user import user_router

app= FastAPI()

origins= [
  'http://localhost/5173',

]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_headers=['*'],
  allow_methods=['*'],

)

app.include_router(auth_router, prefix='/api')
app.include_router(user_router)