"""
Main FastAPI application for the Nonprofit CRM.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

from config import settings
from api.routers import auth, constituents, contributions, interactions, opportunities, dashboard
from api.constituents.briefing import router as briefing_router
from api.routers import segments as segments_router
from api.routers import tasks as tasks_router
from api.routers import voice as voice_router


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive CRM system for nonprofit organizations to manage constituents, donations, and relationships.",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(constituents.router, prefix=settings.API_V1_PREFIX, tags=["Constituents"])
app.include_router(contributions.router, prefix=settings.API_V1_PREFIX, tags=["Contributions"])
app.include_router(interactions.router, prefix=settings.API_V1_PREFIX, tags=["Interactions"])
app.include_router(opportunities.router, prefix=settings.API_V1_PREFIX, tags=["Opportunities"])
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX, tags=["Dashboard"])
app.include_router(briefing_router, prefix=settings.API_V1_PREFIX, tags=["Briefings"])
app.include_router(segments_router.router, prefix=settings.API_V1_PREFIX, tags=["Segments"])
app.include_router(tasks_router.router, prefix=settings.API_V1_PREFIX, tags=["Tasks"])
app.include_router(voice_router.router, prefix=settings.API_V1_PREFIX, tags=["Voice"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
