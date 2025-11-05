"""
Pydantic models for user creation and update requests.

These schemas define the structure of incoming JSON payloads for user
creation and update endpoints. They encapsulate validation logic and
default values so that FastAPI can automatically parse requests and
provide meaningful error messages when the payload is invalid.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """Schema for creating a new user.

    Required fields:
    - username: Unique identifier for the user
    - email: Valid email address
    - password: Plain text password (will be hashed before storage)
    - role: User's role (e.g. ``admin``)

    Optional fields:
    - is_active: Whether the user account should be active upon creation. Defaults to True.
    """

    username: str = Field(..., description="Unique username for the user")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., description="Plain text password (hashed before storage)")
    role: str = Field(..., description="User role (e.g., admin)")
    is_active: Optional[bool] = Field(True, description="Whether the user account is active")


class UserUpdateRequest(BaseModel):
    """Schema for updating an existing user.

    Only the provided fields will be updated. Fields left as None
    will remain unchanged. The ``password`` field, when present,
    should contain the new plain text password; it will be hashed before
    storage.
    """

    email: Optional[EmailStr] = Field(None, description="New email address")
    role: Optional[str] = Field(None, description="New role for the user")
    is_active: Optional[bool] = Field(None, description="Activate or deactivate the user")
    password: Optional[str] = Field(None, description="New plain text password")