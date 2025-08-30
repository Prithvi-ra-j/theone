"""Main FastAPI application for Dristhi."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.routers import auth, career, habits, finance, mood, gamification, memory

# Global variables for lifespan management
ai_service = None
memory_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Dristhi backend...")
    
    # Initialize AI services
    if settings.ENABLE_AI_FEATURES:
        try:
            from app.services.ai_service import AIService
            from app.services.memory_service import MemoryService
            
            global ai_service, memory_service
            ai_service = AIService()
            memory_service = MemoryService()
            
            logger.info("✅ AI services initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ AI services initialization failed: {e}")
            logger.info("AI features will be disabled")
    
    logger.info("✅ Dristhi backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Dristhi backend...")
    
    # Cleanup AI services
    if ai_service:
        try:
            await ai_service.cleanup()
            logger.info("✅ AI services cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up AI services: {e}")
    
    logger.info("✅ Dristhi backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_enabled": settings.ENABLE_AI_FEATURES,
        "ai_service_status": "available" if ai_service else "unavailable",
    }


# Root endpoint
@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }


# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(career.router, prefix=settings.API_V1_STR, tags=["career"])
app.include_router(habits.router, prefix=settings.API_V1_STR, tags=["habits"])
app.include_router(finance.router, prefix=settings.API_V1_STR, tags=["finance"])
app.include_router(mood.router, prefix=settings.API_V1_STR, tags=["mood"])
app.include_router(gamification.router, prefix=settings.API_V1_STR, tags=["gamification"])
app.include_router(memory.router, prefix=settings.API_V1_STR, tags=["memory"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
