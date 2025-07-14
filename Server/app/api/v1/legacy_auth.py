from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.user import User
from ...services.auth_service import AuthService
from ..dependencies import get_current_user

router = APIRouter(tags=["Authentication (legacy)"])

# POST /register
@router.post("/register", status_code=201)
async def register_user(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Legacy registration endpoint expected by the test-suite."""
    auth = AuthService(db)
    try:
        tokens = auth.register_user(payload)
        user = db.query(User).filter(User.username == payload.get("username")).first()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.isActive,
        }
    except HTTPException as e:
        if e.status_code == 400:
            raise
        raise

# POST /token (OAuth2 style)
@router.post("/token")
async def login_for_access_token(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/x-www-form-urlencoded"):
        form = await request.form()
        username = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        body = await request.json()
        username = body.get("username") or body.get("email")
        password = body.get("password")

    auth = AuthService(db)
    # Guard against missing credentials early
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password are required",
        )

    user = auth.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token({"sub": str(user.id), "username": user.username})
    refresh_token = auth.create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# GET /me
@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    } 