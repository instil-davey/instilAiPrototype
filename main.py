"""
Constituent Briefing API - Main Application

FastAPI application providing AI-powered constituent briefings for nonprofit CRM.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api.constituents.briefing import router as briefing_router

# Create FastAPI application
app = FastAPI(
    title="Constituent Briefing API",
    description="""
    AI-powered constituent briefing engine for nonprofit organizations.

    ## Features

    * **AI-Powered Insights**: Uses Claude AI to generate intelligent constituent briefings
    * **Comprehensive Analysis**: Analyzes contributions, interactions, opportunities, and more
    * **Personalized Recommendations**: Provides actionable next steps for each constituent
    * **RESTful API**: Easy integration with existing CRM systems and frontends

    ## Endpoints

    * `GET /api/constituents/{id}/briefing` - Generate briefing for a single constituent
    * `POST /api/constituents/briefings/batch` - Generate briefings for multiple constituents

    ## Setup

    1. Set `ANTHROPIC_API_KEY` environment variable
    2. Ensure database is initialized with constituent data
    3. Run with: `uvicorn main:app --reload`

    ## Authentication

    Not currently implemented. Add authentication middleware as needed for production.
    """,
    version="1.0.0",
    contact={
        "name": "Development Team",
        "email": "dev@example.org"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(briefing_router)


# Root endpoint
@app.get("/", tags=["health"])
async def root():
    """
    API root endpoint - health check and basic info.

    Returns:
        Basic API information and status
    """
    return {
        "name": "Constituent Briefing API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "briefing": "/api/constituents/{constituent_id}/briefing"
        },
        "configuration": {
            "anthropic_api_key_configured": bool(os.getenv('ANTHROPIC_API_KEY')),
            "database_path": os.getenv('DATABASE_URL', 'nonprofit_crm.db')
        }
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Health status and configuration checks
    """
    checks = {
        "api": "healthy",
        "anthropic_api_key": "configured" if os.getenv('ANTHROPIC_API_KEY') else "missing",
    }

    # Check if database exists
    db_path = os.getenv('DATABASE_URL', 'nonprofit_crm.db')
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')

    if os.path.exists(db_path):
        checks["database"] = "available"
    else:
        checks["database"] = "not_found"

    # Determine overall status
    all_healthy = (
        checks["anthropic_api_key"] == "configured" and
        checks["database"] == "available"
    )

    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks
        }
    )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        print()

    # Check for database
    db_path = os.getenv('DATABASE_URL', 'nonprofit_crm.db')
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')

    if not os.path.exists(db_path):
        print(f"WARNING: Database not found at {db_path}")
        print("Run the data ingestion script first: python load_data.py")
        print()

    print("Starting Constituent Briefing API...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
