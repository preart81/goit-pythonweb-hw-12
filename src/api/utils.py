"""
This module contains utility functions for the FastAPI application.
Routes:
    /healthchecker (GET): Checks the health of the database connection.
Functions:
    healthchecker(db: AsyncSession): Asynchronously checks if the database is configured correctly and returns a health check message.
Dependencies:
    db: An asynchronous database session dependency.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Asynchronous health check endpoint to verify database connectivity.
    This function performs an asynchronous query to the database to ensure it is
    configured correctly and can be accessed. If the query fails or returns an
    unexpected result, an HTTP 500 error is raised.
    Args:
        db (AsyncSession): The database session dependency.
    Returns:
        dict: A dictionary containing a health check message if the database is
        accessible.
    Raises:
        HTTPException: If there is an error connecting to the database or if the
        database is not configured correctly.
    """
    try:
        # Виконуємо асинхронний запит
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": messages.HEALTHCHECKER_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        ) from e
