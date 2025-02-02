""" 
This module defines Pydantic models for contact information and related requests.

Classes:
    ContactBase: A base schema for contact information, including fields for first name, last name, email, phone number, birthday, and additional data.
    ContactResponse: Extends ContactBase to include additional fields for id, created_at, and updated_at.
    ContactBirthdayRequest: Represents a request for contact birthdays, including a field for the number of days within which to search for birthdays. 
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactBase(BaseModel):
    """
    ContactBase schema for contact information.
    """

    first_name: str = Field(max_length=50, min_length=2)
    last_name: str = Field(max_length=50, min_length=2)
    email: EmailStr
    phone_number: str = Field(max_length=20, min_length=6)
    birthday: date
    additional_data: Optional[str] = Field(max_length=150)

    @field_validator("birthday")
    def validate_birthday(cls, v):
        """
        Validate the birthday field to ensure that it is not in the future.

        Args:
            v (date): The birthday date to validate.

        Returns:
            date: The validated birthday date.

        Raises:
            ValueError: If the birthday is in the future.
        """

        if v > date.today():
            raise ValueError("Birthday cannot be in the future")
        return v


class ContactResponse(ContactBase):
    """
    ContactResponse is a data model that extends ContactBase and includes additional fields for
    id, created_at, and updated_at.
    """

    id: int
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayRequest(BaseModel):
    """
    ContactBirthdayRequest is a Pydantic model that represents a request for contact birthdays.

    Attributes:
        days (int): The number of days within which to search for birthdays.
                    Must be between 0 and 366 inclusive.
    """

    days: int = Field(ge=0, le=366)
