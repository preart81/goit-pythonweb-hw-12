""" This module defines the database models for the application using SQLAlchemy ORM.
Classes:
    Base: A base class for all models, providing common attributes for creation and update timestamps.
    Contact: A model representing a contact in the database.
    User: A model representing a user in the database.
"""

from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String, Table, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Date, DateTime


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class Contact(Base):
    """
    Contact model representing a contact in the database.

    Attributes:
        id (int): Primary key of the contact.
        first_name (str): First name of the contact. Maximum length is 50 characters.
        last_name (str): Last name of the contact. Maximum length is 50 characters.
        email (str): Email address of the contact. Maximum length is 100 characters.
        phone_number (str): Phone number of the contact. Maximum length is 20 characters.
        birthday (date): Birthday of the contact.
        additional_data (str, optional): Additional data related to the contact. Maximum length is 150 characters.
        user_id (int, optional): Foreign key referencing the user who owns the contact.
        user (User): Relationship to the User model.
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str] = mapped_column(String(150), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class UserRole(Enum):
    """
    Enum representing the roles of a user.
    """

    ADMIN = "admin"
    USER = "user"


class User(Base):
    """
    User model representing a user in the database.

    Attributes:
        id (int): Primary key of the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password of the user.
        created_at (datetime): Timestamp when the user was created.
        avatar (str, optional): URL or path to the user's avatar image.
        confirmed (bool): Indicates whether the user's email is confirmed.

    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(
        SqlEnum(UserRole, create_type=True),
        name="role",
        default=UserRole.USER,
        nullable=False,
    )
