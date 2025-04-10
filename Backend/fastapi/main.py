from fastapi import FastAPI
from fastapi.routes import pets

FastAPI = FastAPI()

#Routes for pet interaction
FastAPI.include_router(pets.router)