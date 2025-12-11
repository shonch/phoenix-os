# manage_users_api.py — FastAPI altar for User Management
from fastapi import FastAPI
from rituals.launcher import users_endpoints

app = FastAPI()

# include the user router
app.include_router(users_endpoints.router, prefix="/users", tags=["users"])
