from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..db.database import get_db
from ..core.config import settings
from ..core.exceptions import UnauthorizedException
from ..models.user import User
from ..services.submission_service import SubmissionService
from ..services.playground.mock_playground_service import MockPlaygroundService
from ..services.playground.real_playground_service import RealPlaygroundService
from ..services.playground.playground_service_factory import PlaygroundServiceFactory
from ..services.playground_execution_interface import IPlaygroundExecutionService

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exception
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_playground_execution_service() -> IPlaygroundExecutionService:
    return MockPlaygroundService()


def get_submission_service(
    db: Session = Depends(get_db),
    playground_executor: IPlaygroundExecutionService = Depends(get_playground_execution_service)
) -> SubmissionService:
    return SubmissionService(db=db, playground_executor=playground_executor)


async def get_real_playground_service() -> IPlaygroundExecutionService:
    return RealPlaygroundService()


def get_mock_playground_service() -> IPlaygroundExecutionService:
    return MockPlaygroundService()
