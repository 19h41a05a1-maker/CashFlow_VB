"""
API v1 endpoints package.
"""

from fastapi import APIRouter

# Import endpoint routers when they are created
# from app.api.v1.endpoints import auth, accounts, credits, holds, debits, reports

router = APIRouter(prefix="/api/v1")

# Include routers when endpoints are created
# router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
# router.include_router(credits.router, prefix="/credits", tags=["Credits"])
# router.include_router(holds.router, prefix="/holds", tags=["Holds"])
# router.include_router(debits.router, prefix="/debits", tags=["Debits"])
# router.include_router(reports.router, prefix="/reports", tags=["Reports"])
