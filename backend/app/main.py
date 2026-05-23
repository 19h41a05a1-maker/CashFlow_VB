"""
FastAPI application factory and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.database.db import init_db, get_db
from app.exceptions.base_exception import BaseException
from app.api.v1.endpoints import auth, accounts, credits, holds, debits, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    settings = get_settings()
    
    # Initialize database
    init_db()
    
    # Create FastAPI app
    app = FastAPI(
        title="Cash Management - 5 Days Hold Checking System",
        description="REST API for managing cash flow with 5-day hold verification",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Add middleware
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS if hasattr(settings, 'ALLOWED_HOSTS') else ["localhost", "127.0.0.1"]
    )
    
    # Include API routes
    app.include_router(auth.router)
    app.include_router(accounts.router)
    app.include_router(credits.router)
    app.include_router(holds.router)
    app.include_router(debits.router)
    app.include_router(reports.router)
    
    # Custom exception handler
    @app.exception_handler(BaseException)
    async def base_exception_handler(request, exc):
        """Handle custom base exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "details": str(exc) if settings.DEBUG else "An error occurred"
                }
            }
        )
    
    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    
    # Ready check endpoint
    @app.get("/api/ready")
    async def ready_check(db: Session = __import__('fastapi').Depends(get_db)):
        """Ready check - verifies database connectivity."""
        try:
            # Test database connection
            db.execute("SELECT 1")
            return {
                "ready": True,
                "database": "connected"
            }
        except Exception as e:
            logger.error(f"Readiness check failed: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={"ready": False, "error": "Database connection failed"}
            )
    
    logger.info(f"FastAPI application created for environment: {settings.ENVIRONMENT}")
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
