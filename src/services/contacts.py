""" This module provides the ContactService class, which offers various methods to manage contacts for a user.
The service interacts with the ContactRepository to perform database operations asynchronously.
Classes:
    ContactService: A service class to handle contact-related operations.
Methods:
    __init__(db: AsyncSession):
    create_contact(body: ContactBase, user: User):
    get_contacts(skip: int, limit: int, user: User):
    get_contact(contact_id: int, user: User):
    update_contact(contact_id: int, body: ContactBase, user: User):
    remove_contact(contact_id: int, user: User):
    search_contacts(search: str, skip: int, limit: int, user: User):
    upcoming_birthdays(days: int, user: User): """

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase, ContactResponse


class ContactService:
    """
    ContactService provides methods to manage contacts for a given user.
    Methods:
        __init__(db: AsyncSession):
        create_contact(body: ContactBase, user: User) -> ContactResponse:
        get_contacts(skip: int, limit: int, user: User) -> List[ContactResponse]:
        get_contact(contact_id: int, user: User) -> Contact | None:
        update_contact(contact_id: int, body: ContactBase, user: User) -> ContactResponse | None:
        remove_contact(contact_id: int, user: User) -> ContactResponse | None:
        search_contacts(search: str, skip: int, limit: int, user: User) -> List[ContactResponse]:
        upcoming_birthdays(days: int, user: User) -> List[ContactResponse]:
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactService with a database session.

        Args:
            db (AsyncSession): The database session to use for operations.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Creates a new contact for a given user.

        Args:
            body (ContactBase): The contact details to be created.
            user (User): The user to whom the contact belongs.

        Returns:
            ContactResponse: The newly created contact instance.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Retrieves a list of contacts for a given user with pagination.

        Args:
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return.
            user (User): The user for which to retrieve the contacts.

        Returns:
            List[ContactResponse]: A list of contacts for the given user.
        """

        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user for which to retrieve the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """

        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Updates a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The contact details to be updated.
            user (User): The user to whom the contact belongs.

        Returns:
            ContactResponse | None: The updated contact if found, otherwise None.
        """

        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Removes a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user to whom the contact belongs.

        Returns:
            ContactResponse | None: The removed contact if found, otherwise None.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(self, search: str, skip: int, limit: int, user: User):
        """
        Searches for contacts based on a search string with pagination for a given user.

        Args:
            search (str): The search string to search for in contacts.
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return.
            user (User): The user for which to search contacts.

        Returns:
            List[ContactResponse]: A list of contacts that match the search criteria.
        """
        return await self.contact_repository.search_contacts(search, skip, limit, user)

    async def upcoming_birthdays(self, days: int, user: User):
        """
        Fetches a list of contacts with upcoming birthdays within the specified number of days for a given user.

        Args:
            days (int): The number of days in the future to search for upcoming birthdays.
            user (User): The user whose contacts are being queried.

        Returns:
            List[ContactResponse]: A list of contacts with birthdays within the specified number of days.
        """

        return await self.contact_repository.upcoming_birthdays(days, user)
