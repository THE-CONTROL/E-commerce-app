from fastapi import FastAPI
from app.routes.user import user_router
from app.routes.auth import auth_router
from app.routes.account import account_router


app = FastAPI(
    title="Your API",
    description="API Documentation",
    version="1.0.0",
)

# Include routers
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(account_router)

