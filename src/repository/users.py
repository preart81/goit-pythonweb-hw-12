"""
Repository for the User model.

This repository provides methods to interact with the User model in the database
using asynchronous SQLAlchemy sessions.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate


class UserRepository:
    """
    UserRepository provides methods to interact with the User table in the database.
    Methods:
        __init__(session: AsyncSession):
            Initializes the UserRepository with a database session.
        get_user_by_id(user_id: int) -> User | None:
            Retrieves a user by their ID.
        get_user_by_username(username: str) -> User | None:
            Retrieves a user by their username.
        get_user_by_email(email: str) -> User | None:
            Retrieves a user by their email address.
        create_user(body: UserCreate, avatar: str = None) -> User:
            Creates a new user in the database.
        confirmed_email(email: str) -> None:
            Confirms the user's email address.
        update_avatar_url(email: str, url: str) -> User:
            Updates the avatar URL of the user with the given email address.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the UserRepository with a database session.
        Args:
            session (AsyncSession): The database session to use for operations.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieves a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """Creates a new user in the database.

        Args:
            body (UserCreate): The user details to be created.
            avatar (str, optional): The URL or path to the user's avatar image.

        Returns:
            User: The newly created user instance.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """Confirms the user's email address.

        Args:
            email (str): The email address to be confirmed.

        Returns:
            None: No return value.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """Updates the avatar URL of the user with the given email address.

        Args:
            email (str): The email address of the user to update.
            url (str): The new avatar URL to be updated.

        Returns:
            User: The updated user instance.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
