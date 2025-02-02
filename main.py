""" Main file to run the contact management application. """

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.api import auth, contacts, users, utils
from src.conf import messages

app = FastAPI()
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

origins = ["<http://localhost:8000>"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles rate limit exceeded exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (RateLimitExceeded): The exception raised when the rate limit is exceeded.

    Returns:
        JSONResponse: A JSON response with a 429 status code and an error message indicating that the rate limit has been exceeded.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": f"Перевищено ліміт запитів ({exc.detail}). Спробуйте пізніше."
        },
    )


@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing the welcome message.
    """
    return {"message": messages.WELCOME_MESSAGE}


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
