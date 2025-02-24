from fastapi import FastAPI
from app.routes.user import user_router
from app.routes.auth import auth_router
from app.routes.account import account_router
from app.routes.password import password_reset_router
from app.routes.admin import admin_router
from app.routes.product import product_router
from app.routes.store import store_router
from app.routes.transaction import transaction_router
import uvicorn

app = FastAPI(
    title="E commerce app API",
    description="API Documentation",
    version="1.0.0",
)

# Include routers
app.include_router(account_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(password_reset_router)
app.include_router(product_router)
app.include_router(store_router)
app.include_router(transaction_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)