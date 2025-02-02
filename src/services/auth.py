""" 
This module provides authentication services including password hashing, JWT token creation, and user retrieval.

Classes:
    Hash: Provides methods for hashing and verifying passwords using bcrypt.
Functions:
    create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    create_email_token(data: dict) -> str:
    get_email_from_token(token: str) -> str: 
"""

from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.services.users import UserService


class Hash:
    """
    Hash class provides methods for hashing and verifying passwords using bcrypt.
    Attributes:
        pwd_context (CryptContext): The context for password hashing and verification.
    Methods:
        verify_password(plain_password, hashed_password):
            Verifies a plain password against a hashed password.
        get_password_hash(password: str):
            Returns the hashed version of the given password.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies a plain password against a hashed password.
        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to verify against.
        Returns:
            bool: Whether the passwords match.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Returns the hashed version of the given password.
        Args:
            password (str): The password to hash.
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Creates a new access token for the given data.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[int]): The expiration time in seconds from now. Defaults to settings.JWT_EXPIRATION_SECONDS.

    Returns:
        str: The generated access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    # print(to_encode)
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Gets the current user using the JWT token in the Authorization header.

    Args:
        token (HTTPAuthorizationCredentials): The JWT token in the Authorization header.
        db (Session): The database session dependency.

    Returns:
        User: The current user if the token is valid, otherwise raises an HTTPException with a 401 status code.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        # print(payload)
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
    """
    Creates a new JWT token for the given data that will expire in 7 days.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The generated JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Extracts the email from the given JWT token.

    Args:
        token (str): The JWT token containing the email.

    Returns:
        str: The email extracted from the token.

    Raises:
        HTTPException: If the token is invalid or the email is not found.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Невірний токен для перевірки електронної пошти",
        )
