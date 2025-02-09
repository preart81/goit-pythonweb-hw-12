"""
Registers a new user by saving their details to the database.

Args:
    user_data (UserCreate): The user details for registration.

Returns:
    User: The registered user object.

Raises:
    HTTPException: If a user with the given email already exists.
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import RequestEmail, Token, User, UserCreate, UserLogin
from src.services.auth import Hash, create_access_token, get_email_from_token
from src.services.email import send_email
from src.services.users import UserService
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])


# Реєстрація користувача
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Registers a new user in the system.
    Args:
        user_data (UserCreate): The data required to create a new user.
        background_tasks (BackgroundTasks): Background tasks to be executed after the user is registered.
        request (Request): The HTTP request object.
        db (Session, optional): The database session dependency.
    Raises:
        HTTPException: If a user with the given email already exists.
        HTTPException: If a user with the given username already exists.
    Returns:
        User: The newly created user.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.API_ERROR_USER_ALREADY_EXIST,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    """
    Logs in a user by verifying their email and password, and returns an access token.
    Args:
        body (UserLogin): The login details provided by the user, including email and password.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).
    Raises:
        HTTPException: If the user is not confirmed.
        HTTPException: If the user does not exist or the password is incorrect.
    Returns:
        dict: A dictionary containing the access token and token type.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.API_ERROR_USER_NOT_AUTHORIZED,
        )
    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.API_ERROR_WRONG_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handles the request to send a confirmation email to the user.
    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): The background tasks manager to handle asynchronous tasks.
        request (Request): The HTTP request object.
        db (Session, optional): The database session dependency.
    Returns:
        dict: A message indicating the status of the email confirmation request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": messages.API_EMAIL_CONFIRMED}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm the user's email address using the provided token.

    Args:
        token (str): The token used to confirm the email address.
        db (Session, optional): The database session dependency.

    Returns:
        dict: A message indicating the result of the email confirmation.

    Raises:
        HTTPException: If the user is not found or the verification fails.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": messages.API_EMAIL_CONFIRMED}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


# скидання пароля
@router.post("/reset_password")
async def reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handles the request to reset the user's password.
    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): The background tasks manager for asynchronous tasks.
        request (Request): The HTTP request object.
        db (Session, optional): The database session dependency.
    Returns:
        dict: A message indicating the status of the password reset request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url, type="reset"
        )
    return {"message": "Перевірте свою електронну пошту для скидання пароля"}

# зміна пароля
@router.patch("/update_password/{token}")
async def update_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """
    Changes the user's password using the provided token.
    Args:
        token (str): The token used to change the password.
        password (str): The new password.
        db (Session, optional): The database session dependency.
    Returns:
        dict: A message indicating the result of the password change.
    Raises:
        HTTPException: If the user is not found or the password change fails.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    new_password = Hash().get_password_hash(new_password)
    await user_service.update_password(email, new_password)
    return {"message": "Пароль успішно змінено"}
