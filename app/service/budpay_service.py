# app/service/budpay_service.py
from typing import Dict
import httpx
from fastapi import HTTPException, status
from app.core.config import BUDPAY_SECRET_KEY
from decimal import Decimal

class BudpayService:
    def __init__(self):
        self.api_key = BUDPAY_SECRET_KEY
        self.base_url = "https://api.budpay.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_virtual_account(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: str
    ) -> Dict:
        """Create a virtual account in Budpay"""
        try:
            payload = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/virtual-account/create",
                    json=payload,
                    headers=self.headers
                )
                
                response_data = response.json()
                
                if response.status_code != 200 or not response_data.get("status"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=response_data.get("message", "Virtual account creation failed")
                    )
                    
                return response_data["data"]
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to payment service"
            )

    async def verify_payment(self, reference: str) -> Dict:
        """Verify payment status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transaction/verify/{reference}",
                    headers=self.headers
                )
                
                response_data = response.json()
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=response_data.get("message", "Payment verification failed")
                    )
                    
                return response_data["data"]
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to payment service"
            )

    def verify_webhook_signature(self, signature: str, payload: bytes) -> bool:
        """Verify Budpay webhook signature"""
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            BUDPAY_SECRET_KEY.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    async def get_virtual_account_balance(self, account_number: str) -> Dict:
        """Get virtual account balance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/virtual-account/balance/{account_number}",
                    headers=self.headers
                )
                
                response_data = response.json()
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=response_data.get("message", "Balance check failed")
                    )
                    
                return response_data["data"]
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to payment service"
            )
