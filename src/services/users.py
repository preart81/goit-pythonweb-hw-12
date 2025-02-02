from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate


class UserService:
    """
    UserService class provides methods to interact with user data in the database.
    Methods
    -------
    __init__(db: AsyncSession)
        Initializes the UserService with a database session.
    create_user(body: UserCreate)
        Creates a new user with the provided data and generates an avatar using Gravatar.
    get_user_by_id(user_id: int)
        Retrieves a user by their unique ID.
    get_user_by_username(username: str)
        Retrieves a user by their username.
    get_user_by_email(email: str)
        Retrieves a user by their email address.
    confirmed_email(email: str) -> None
        Confirms the user's email address.
    update_avatar_url(email: str, url: str)
        Updates the user's avatar URL.
    """

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Asynchronously creates a new user with the provided details.
        This method attempts to generate a Gravatar image for the user's email.
        If the Gravatar generation fails, it catches the exception and proceeds
        without an avatar.
        Args:
            body (UserCreate): An instance of UserCreate containing the user's details.
        Returns:
            The created user object with the avatar if available.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            User: The user object corresponding to the provided ID.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object corresponding to the given username.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Asynchronously retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User: The user object corresponding to the given email address, or None if no user is found.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Confirms the email address of a user.

        Args:
            email (str): The email address to be confirmed.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Asynchronously updates the avatar URL for a user identified by their email.

        Args:
            email (str): The email address of the user whose avatar URL is to be updated.
            url (str): The new avatar URL to be set for the user.

        Returns:
            bool: True if the avatar URL was successfully updated, False otherwise.
        """
        return await self.repository.update_avatar_url(email, url)
