""" 
This module defines the `ContactRepository` class, which provides methods for
managing contacts in the database. 
"""

from datetime import timedelta
from typing import List

from sqlalchemy import Integer, and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact, User
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    """
    Repository class for managing contacts in the database.
    Methods:
    --------
    __init__(self, session: AsyncSession):
        Initializes the repository with a database session.
        Retrieves a list of contacts for a given user with pagination.
        Retrieves a contact by its ID for a given user.
        Creates a new contact for a given user.
        Removes a contact by its ID for a given user.
    async def update_contact(self, contact_id: int, body: ContactBase, user: User) -> Contact | None:
        Updates a contact by its ID for a given user.
    async def search_contacts(self, search: str, skip: int, limit: int, user: User) -> List[Contact]:
        Searches for contacts based on a search string with pagination for a given user.
        Retrieves a list of contacts with upcoming birthdays within a specified number of days for a given user.
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieves a list of contacts for a given user with pagination.
        Args:
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return.
            user (User): The user for which to retrieve the contacts.
        Returns:
            List[Contact]: A list of contacts for the given user.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieves a contact by its ID for a given user.
        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user for which to retrieve the contact.
        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Creates a new contact for a given user.

        Args:
            body (ContactBase): The contact details to be created.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact: The newly created contact instance.
        """

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Removes a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact | None: The removed contact if found, otherwise None.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Updates an existing contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The contact details to be updated.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Searches for contacts based on a search query for a given user.

        Args:
            search (str): The search query.
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            user (User): The user to whom the contacts belong.

        Returns:
            List[Contact]: A list of contacts matching the search query.
        """
        stmt = (
            select(Contact)
            .filter(
                Contact.user == user,
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.additional_data.ilike(f"%{search}%"),
                    Contact.phone_number.ilike(f"%{search}%"),
                ),
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Retrieves a list of contacts with upcoming birthdays within a specified number of days for a given user.

        Args:
            days (int): The number of days in the future to search for upcoming birthdays.
            user (User): The user whose contacts are being queried.

        Returns:
            List[Contact]: A list of contacts whose birthdays fall within the specified number of days.
        """

        today = func.current_date()
        future_date = func.current_date() + timedelta(days=days)

        stmt = select(Contact).filter(
            Contact.user == user,
            or_(
                func.make_date(
                    extract("year", today).cast(Integer),
                    extract("month", Contact.birthday).cast(Integer),
                    extract("day", Contact.birthday).cast(Integer),
                ).between(today, future_date),
                func.make_date(
                    (extract("year", today) + 1).cast(Integer),
                    extract("month", Contact.birthday).cast(Integer),
                    extract("day", Contact.birthday).cast(Integer),
                ).between(today, future_date),
            ),
        )
        # print((stmt))
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
