from fastapi import FastAPI
from app.routes.user import user_router
from app.routes.auth import auth_router
from app.routes.account import account_router
from app.routes.password import password_reset_router


app = FastAPI(
    title="Your API",
    description="API Documentation",
    version="1.0.0",
)

# Include routers
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(password_reset_router)

"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHBpcmVzIjoxNzQwMTQzNDQzLjAzNTcyM30.e9owiRV_GPyRHBhvsLs34OwtGfjHvh8M6GOva_IPNO8"