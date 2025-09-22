"""Main FastAPI application for Dristhi."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from loguru import logger
import os

from app.core.config import settings
from app.routers import auth, career, habits, finance, mood, gamification, memory, mini_assistant

# Global variables for lifespan management
ai_service = None
memory_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Dristhi backend...")
    # Log configured CORS origins for debugging CORS preflight issues
    try:
        logger.info("Configured BACKEND_CORS_ORIGINS: %s", settings.BACKEND_CORS_ORIGINS)
    except Exception:
        logger.info("Could not read BACKEND_CORS_ORIGINS from settings")
    
    # Initialize AI services
    if settings.ENABLE_AI_FEATURES:
        try:
            from app.services.ai_service import AIService
            from app.services.memory_service import MemoryService
            
            global ai_service, memory_service
            # Create service objects but do not block on network calls. Schedule
            # the potentially slow initialization to run in the background so
            # the app can start serving requests immediately.
            ai_service = AIService()
            memory_service = MemoryService()

            # Schedule async initialization of the AI service in the event loop.
            try:
                import asyncio

                asyncio.create_task(ai_service.initialize())
                logger.info("ℹ️ AI service initialization scheduled in background")
            except Exception:
                logger.warning("⚠️ Could not schedule AI service initialization")

            logger.info("✅ AI service objects created (initialization deferred)")
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
# Use configured BACKEND_CORS_ORIGINS explicitly. Do not use '*' with
# allow_credentials=True because Starlette will reject that combination.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Accept common local development origins (both localhost and 127.0.0.1) via regex so
    # frontend dev servers running on different ports don't trigger CORS preflight failures.
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
)


# Dynamic CORS fallback middleware
# If the environment has not been configured with explicit BACKEND_CORS_ORIGINS,
# this middleware will echo the incoming Origin header into the Access-Control-Allow-Origin
# response header when either DEBUG is true or ALLOW_CORS_FROM_REQUEST=1 is set.
# This is a development-friendly fallback and should be used with caution in production.
@app.middleware("http")
async def dynamic_cors_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        origin = request.headers.get("origin")
        # Only set dynamic CORS in debug or when explicitly allowed via env
        allow_dynamic = bool(settings.DEBUG) or os.getenv("ALLOW_CORS_FROM_REQUEST", "0") == "1"
        if origin and allow_dynamic and "access-control-allow-origin" not in (k.lower() for k in response.headers.keys()):
            response.headers["Access-Control-Allow-Origin"] = origin
            # Ensure Vary so caches know responses vary by Origin
            response.headers["Vary"] = response.headers.get("Vary", "Origin")
            # Common CORS headers to allow browser requests from frontend apps
            response.headers.setdefault("Access-Control-Allow-Headers", "Authorization,Content-Type")
            response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    except Exception:
        # Be defensive: do not break request flow on middleware errors
        logger.exception("Error in dynamic CORS middleware")
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    # If the exception is an HTTPException with detail, preserve it.
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
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
app.include_router(career.router, prefix=f"{settings.API_V1_STR}/career", tags=["career"])
# Register habits under /api/v1/habits so frontend paths like /api/v1/habits/dashboard
# and /api/v1/habits/tasks resolve correctly.
app.include_router(habits.router, prefix=f"{settings.API_V1_STR}/habits", tags=["habits"])
app.include_router(finance.router, prefix=f"{settings.API_V1_STR}/finance", tags=["finance"])
app.include_router(__import__("app.routers.ai", fromlist=["router"]).router, prefix=settings.API_V1_STR, tags=["ai"])
# Register mood and gamification under their own subpaths so routes
# are reachable at /api/v1/mood/* and /api/v1/gamification/* respectively.
app.include_router(mood.router, prefix=f"{settings.API_V1_STR}/mood", tags=["mood"])
app.include_router(gamification.router, prefix=f"{settings.API_V1_STR}/gamification", tags=["gamification"])
app.include_router(memory.router, prefix=settings.API_V1_STR, tags=["memory"])
# Mini Assistant router
from app.routers.mini_assistant import router as mini_assistant_router
app.include_router(mini_assistant_router, prefix=f"{settings.API_V1_STR}/mini-assistant", tags=["mini-assistant"])
# Demo auth route for quick prototype login (enabled via ENABLE_DEMO_LOGIN env var)
try:
    from app.routers.demo_auth import router as demo_auth_router
    app.include_router(demo_auth_router, prefix=settings.API_V1_STR, tags=["demo-auth"])
except Exception as _:
    # Do not fail startup if demo router import fails
    pass
# Optional mock endpoints for frontend development
if settings.ENABLE_MOCK_ENDPOINTS:
    try:
        from app.routers.mocks_core import router as mocks_router

        app.include_router(mocks_router, prefix=settings.API_V1_STR, tags=["mocks"])
    except Exception as e:
        # Don't block startup if mock router fails to import
        logger.warning(f"Failed to include mock endpoints: {e}")

# Compatibility router (development only): placed after real routers so it
# only handles requests that would otherwise 404. Returns 501 with details.
if settings.ENABLE_COMPATIBILITY_STUBS:
    try:
        from app.routers.compatibility import router as compatibility_router

        app.include_router(compatibility_router, prefix=settings.API_V1_STR, tags=["compat"])
    except Exception:
        # Avoid breaking startup if the compatibility module cannot be imported
        # (e.g., in production where you might remove it).
        pass


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
