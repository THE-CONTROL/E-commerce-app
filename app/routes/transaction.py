# app/routes/transaction_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from app.core.auth_dependency import get_current_user
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.utils.database import get_db
from app.service.transaction_service import TransactionService
from app.data.schemas.transaction_schemas import (
    TransactionRead,
    TransactionListResponse,
    TransactionResponse
)
from app.data.models.transaction_models import TransactionType, TransactionStatus

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="List Transactions",
    description="Get all transactions for authenticated user"
)
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    transaction_type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    db: Session = Depends(get_db),
    current_user: ProtectedUser = Depends(get_current_user)
):
    try:
        transaction_service = TransactionService(session=db)
        result = transaction_service.get_transaction_history(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            type=transaction_type,
            status=status
        )
        return TransactionListResponse(
            message="Transactions retrieved successfully",
            data=result["data"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.get(
    "/{transaction_id}",
    response_model=TransactionRead,
    summary="Get Transaction",
    description="Get specific transaction details"
)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: ProtectedUser = Depends(get_current_user)
):
    try:
        transaction_service = TransactionService(session=db)
        return transaction_service.get_transaction(
            transaction_id=transaction_id,
            user_id=current_user.id
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.get(
    "/account/{account_id}",
    response_model=TransactionListResponse,
    summary="Account Transactions",
    description="Get all transactions for specific account"
)
async def get_account_transactions(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    transaction_type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    db: Session = Depends(get_db),
    current_user: ProtectedUser = Depends(get_current_user)
):
    try:
        transaction_service = TransactionService(session=db)
        result = transaction_service.get_account_transactions(
            account_id=account_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            type=transaction_type,
            status=status
        )
        return TransactionListResponse(
            message="Transactions retrieved successfully",
            data=result["data"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.post(
    "/pay/product/{product_id}",
    response_model=TransactionResponse,
    summary="Pay for Product",
    description="Process payment for product purchase"
)
async def pay_for_product(
    product_id: int,
    store_account_id: int = Body(..., embed=True),
    amount: Decimal = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: ProtectedUser = Depends(get_current_user)
):
    try:
        transaction_service = TransactionService(session=db)
        result = await transaction_service.process_product_payment(
            buyer_account_id=current_user.account_id,
            store_account_id=store_account_id,
            product_id=product_id,
            amount=amount
        )
        return TransactionResponse(
            message="Product payment processed successfully",
            data=result["data"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.post(
    "/pay/subscription/store/{store_id}",
    response_model=TransactionResponse,
    summary="Pay for Store Subscription",
    description="Process payment for store subscription"
)
async def pay_store_subscription(
    store_id: int,
    amount: Decimal = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: ProtectedUser = Depends(get_current_user)
):
    try:
        transaction_service = TransactionService(session=db)
        result = await transaction_service.process_subscription_payment(
            user_account_id=current_user.account_id,
            store_id=store_id,
            amount=amount
        )
        return TransactionResponse(
            message="Subscription payment processed successfully",
            data=result["data"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

# Initialize routers
transaction_router = router