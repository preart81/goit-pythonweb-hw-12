"""
This module defines the API routes for user-related operations.
Routes:
    - GET /users/me: Retrieve the current user's information.
    - PATCH /users/avatar: Update the current user's avatar.
Dependencies:
    - FastAPI dependencies for routing and request handling.
    - SlowAPI for rate limiting.
    - SQLAlchemy for asynchronous database sessions.
    - Custom services and schemas for user authentication, file upload, and user management.
Functions:
    - me(request: Request, user: User): Retrieve the current user's information.
    - update_avatar_user(file: UploadFile, user: User, db: AsyncSession): Update the current user's avatar.
"""

from fastapi import APIRouter, Depends, File, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas.users import User
from src.services.auth import get_current_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Handles the 'me' endpoint to return the current authenticated user.

    Args:
        request (Request): The HTTP request object.
        user (User, optional): The current authenticated user, injected by dependency.

    Returns:
        User: The current authenticated user.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the current user.
    Args:
        file (UploadFile): The new avatar file to be uploaded.
        user (User): The current user, obtained from the dependency injection.
        db (AsyncSession): The database session, obtained from the dependency injection.
    Returns:
        User: The updated user with the new avatar URL.
    Raises:
        HTTPException: If there is an error during the file upload or database update.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
