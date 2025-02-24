# app/core/constants.py
from enum import Enum
from typing import Dict

class SubscriptionType(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class DurationType(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

SUBSCRIPTION_PLANS: Dict[str, Dict] = {
    "basic": {
        "id": 1,
        "type": "basic",
        "name": "Basic Store",
        "description": "Essential features for small businesses",
        "monthly_amount": 29.99,
        "yearly_amount": 299.99,
        "features": ["Basic analytics", "Up to 100 products", "Email support"]
    },
    "premium": {
        "id": 2,
        "type": "premium",
        "name": "Premium Store",
        "description": "Advanced features for growing businesses",
        "monthly_amount": 99.99,
        "yearly_amount": 999.99,
        "features": ["Advanced analytics", "Unlimited products", "Priority support", "Custom domain"]
    },
    "enterprise": {        
        "id": 3,
        "type": "enterprise",
        "name": "Enterprise Store",
        "description": "Complete solution for large businesses",
        "monthly_amount": 299.99,
        "yearly_amount": 2999.99,
        "features": ["Enterprise analytics", "Unlimited everything", "24/7 support", "Custom solutions"]
    }
}