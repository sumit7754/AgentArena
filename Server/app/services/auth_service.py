from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..core.config import settings
from ..core.exceptions import UnauthorizedException
from ..models.user import User
from ..models.enums import UserRole
import uuid
from sqlalchemy.exc import IntegrityError

class AuthService:
    """Authentication utilities.

    This service can be instantiated **with or without** a SQLAlchemy session.  
    When a database session is supplied it will be used for methods that need
    persistence (register_user/login_user).  The stateless crypto / JWT helper
    methods work without it – this allows the unit-test suite to create an
    instance with no arguments, matching its expectations.
    """

    def __init__(self, db: Session | None = None):
        self._db = db
        self._password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # -------------------------------------------------------------------------
    # Password helpers (public)
    # -------------------------------------------------------------------------

    def get_password_hash(self, password: str) -> str:
        """Hash a plaintext password."""
        return self._password_context.hash(password)

    def verify_password(self, password: str, hashed_pass: str) -> bool:
        """Verify a plaintext password against its hash."""
        return self._password_context.verify(password, hashed_pass)

    # Backwards-compat aliases
    _get_hashed_password = get_password_hash  # legacy private name
    _verify_password = verify_password

    # -------------------------------------------------------------------------
    # JWT helpers (public)
    # -------------------------------------------------------------------------

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a signed JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM) 

    # Legacy private aliases used by existing controller code
    _create_access_token = staticmethod(lambda sub: AuthService().create_access_token({"sub": str(sub)}))  # type: ignore
    _create_refresh_token = staticmethod(lambda sub: AuthService().create_refresh_token({"sub": str(sub)}))  # type: ignore

    def verify_token(self, token: str) -> dict:
        """Decode and validate a JWT, returning its payload."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.JWTError as e:
            raise UnauthorizedException("Invalid token") from e

    # ---------------------------------------------------------------------
    # DB-backed operations (require self._db)
    # ---------------------------------------------------------------------

    def _require_db(self):
        if self._db is None:
            raise RuntimeError("AuthService was instantiated without a database session for an operation that requires one.")

    def register_user(self, user_data: dict) -> dict:
        """Register a new user.

        Rules enforced (per updated requirements):
        1. *username* is **mandatory** and cannot be empty/NULL.
        2. *username* **or** *email* must be unique – duplicates raise **400**.
        3. Any other unhandled exception still bubbles up as **500**.
        """
        self._require_db()

        # ------------------------------------------------------------------
        # Pre-flight duplicate check – fast-fail before hitting DB constraints
        # ------------------------------------------------------------------
        raw_username: str | None = user_data.get("username")
        username_normalized = str(raw_username).strip() if raw_username is not None else None
            
        existing_user = (
            self._db.query(User)
            .filter(or_(User.username == username_normalized, User.email == user_data["email"]))
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already registered")

        # ------------------------------------------------------------------
        # Validate input (after duplicate check)
        # ------------------------------------------------------------------
        if not raw_username or username_normalized == "":
            raise HTTPException(status_code=400, detail="Username is required and cannot be blank")

        username = username_normalized

        # ------------------------------------------------------------------
        # Persist new user
        # ------------------------------------------------------------------
        new_user = User(
            username=username,
            email=user_data["email"],
            password=self._get_hashed_password(user_data["password"]),
            firstName=user_data.get("firstName"),
            lastName=user_data.get("lastName"),
            role=user_data.get("role", UserRole.USER),
        )
            
        self._db.add(new_user)

        try:
            self._db.commit()
        except IntegrityError:
            # Rollback and translate to user-facing validation error (400)
            self._db.rollback()
            raise HTTPException(status_code=400, detail="Username or email already registered")
        except Exception:
            # Rollback for any other DB error and re-raise below
            self._db.rollback()
            raise

        self._db.refresh(new_user)

        return {
            "access_token": self._create_access_token(new_user.id),
            "refresh_token": self._create_refresh_token(new_user.id),
            "token_type": "bearer",
            "role": str(new_user.role),
        }

    def login_user(self, email: str, password: str) -> dict:
        try:
            self._require_db()
            user = self._db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

            if not self._verify_password(password, user.password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

        
            user.lastLoginAt = datetime.utcnow()
            user.loginCount += 1
            self._db.commit()

            return {
                "access_token": self._create_access_token(user.id),
                "refresh_token": self._create_refresh_token(user.id),
                "token_type": "bearer",
                "role": str(user.role),
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        try:
            self._require_db()
            
            # Verify the refresh token
            payload = self.verify_token(refresh_token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Get user from database
            user = self._db.query(User).filter(User.id == str(user_id)).first()
            if not user or not user.isActive:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            # Generate new tokens
            return {
                "access_token": self._create_access_token(user.id),
                "refresh_token": self._create_refresh_token(user.id),
                "token_type": "bearer",
                "role": str(user.role),
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    # ------------------------------------------------------------------
    # Additional helper methods required by unit tests
    # ------------------------------------------------------------------

    def authenticate_user(self, db: Session, username: str, password: str):
        """Authenticate by username and password, returning the user or None."""
        # Accept either username or email for convenience
        user = db.query(User).filter(or_(User.username == username, User.email == username)).first()
        if not user:
            return None
        if not user.isActive:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    def get_user_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
