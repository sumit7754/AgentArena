from fastapi import APIRouter, Depends, Request, Body, HTTPException, status
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...controllers.auth_controller import AuthController
from ...schemas.auth_schema import UserRegisterRequest, UserLoginRequest, TokenResponse, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Preflight support
@router.options("/{any_path:path}")
async def options_handler():
    return {"status": "ok"}

@router.post("/register", response_model=TokenResponse)
async def register(request: dict = Body(...), db: Session = Depends(get_db)):
    controller = AuthController(db)
    # convert dict to schema (optional fields)
    schema = UserRegisterRequest(**request)
    return await controller.register(schema)

@router.post("/login", response_model=TokenResponse)
async def login(request: dict = Body(...), db: Session = Depends(get_db)):
    controller = AuthController(db)
    schema = UserLoginRequest(**request)
    return await controller.login(schema)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    controller = AuthController(db)
    return await controller.refresh_token(request.refresh_token)