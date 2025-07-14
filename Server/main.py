from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core import logging as app_logging  # Initialize logging
from app.core.exceptions import (
    AgentArenaException, 
    NotFoundException, 
    UnauthorizedException, 
    ValidationException,
    PlaygroundExecutionException,
    DatabaseException
)
from app.db.database import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.legacy_auth import router as legacy_auth_router
from app.api.v1 import tasks, agents, submission, admin
from app.api.v1 import playground

from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests."""
    
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
        debug=settings.DEBUG,
        description="AgentArena API for AI agent evaluation in custom playground environments",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

    # Exception handlers
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": exc.message,
                "error_code": exc.error_code
            }
        )

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "message": exc.message,
                "error_code": exc.error_code
            }
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation Error",
                "message": exc.message,
                "error_code": exc.error_code
            }
        )

    @app.exception_handler(PlaygroundExecutionException)
    async def playground_exception_handler(request: Request, exc: PlaygroundExecutionException):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Playground Execution Error",
                "message": exc.message,
                "error_code": exc.error_code
            }
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database Error",
                "message": exc.message,
                "error_code": exc.error_code
            }
        )

    @app.exception_handler(AgentArenaException)
    async def generic_exception_handler(request: Request, exc: AgentArenaException):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": exc.message,
                "error_code": exc.error_code
            }
        )

    # Include routers
    app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
    app.include_router(legacy_auth_router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
    app.include_router(submission.router, prefix="/api/v1", tags=["Submissions"])
    app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
    app.include_router(playground.router, prefix="/api/v1", tags=["Playground"])

    @app.on_event("startup")
    async def startup():
        try:
            # Initialize database without forcing recreation
            init_db(force_recreate=False)
            
            # Ensure default admin exists
            from app.services.auth_service import AuthService
            from app.models.user import UserRole, User
            from app.db.database import SessionLocal
            db = SessionLocal()
            try:
                admin_user = db.query(User).filter(User.email == "sumit@gmail.com").first()
                if not admin_user:
                    auth = AuthService(db)
                    auth.register_user({
                        "username": "admin",
                        "email": "sumit@gmail.com",
                        "password": "sumit@12345",
                        "role": UserRole.ADMIN,
                        "firstName": "Sumit",
                        "lastName": "Admin"
                    })
                    logger.info("Default admin created: sumit@gmail.com")
                else:
                    logger.info("Default admin already exists")
            except Exception as e:
                logger.error(f"Error checking/creating admin user: {str(e)}")
            finally:
                db.close()
                
            logger.info(f"Starting AgentArena in {settings.ENVIRONMENT} environment")
            logger.info("AgentArena playground ready with refactored architecture")
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}")
            raise e

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app_name": "AgentArena",
            "environment": settings.ENVIRONMENT,
            "version": settings.API_VERSION,
            "features": {
                "playground_execution": "mock",  # Will be "live" when implemented
                "agent_evaluations": True,
                "dependency_injection": True,
                "structured_logging": True,
                "exception_handling": True
            }
        }

    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )