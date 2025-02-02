from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


# Схема користувача
class User(BaseModel):
    """
    User model representing a user entity.
    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        avatar (str): URL or path to the user's avatar image.
    Config:
        model_config (ConfigDict): Configuration dictionary with attributes settings.
    """

    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


# Схема для запиту реєстрації
class UserCreate(BaseModel):
    """
    UserCreate schema for creating a new user.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password for the user.
    """

    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """
    UserLogin schema for user login details.

    Attributes:
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    email: str
    password: str


# Схема для токену
class Token(BaseModel):
    """
    Token schema for representing an authentication token.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of the token (e.g., "Bearer").
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    RequestEmail schema for validating email input.

    Attributes:
        email (EmailStr): A valid email address.
    """

    email: EmailStr
