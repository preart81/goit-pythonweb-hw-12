"""
This module defines the configuration settings for the application using Pydantic's BaseSettings.
"""

from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings configuration class for the application.
    Attributes:
        DB_URL (str): Database connection URL.
        JWT_SECRET (str): Secret key for JWT encoding and decoding.
        JWT_ALGORITHM (str): Algorithm used for JWT encoding. Default is "HS256".
        JWT_EXPIRATION_SECONDS (int): Expiration time for JWT tokens in seconds. Default is 3600.
        MAIL_USERNAME (str): Username for the mail server.
        MAIL_PASSWORD (str): Password for the mail server.
        MAIL_FROM (str): Email address to use as the sender.
        MAIL_PORT (int): Port number for the mail server.
        MAIL_SERVER (str): Mail server address.
        MAIL_FROM_NAME (str): Name to use as the sender.
        MAIL_STARTTLS (bool): Whether to use STARTTLS for the mail server. Default is False.
        MAIL_SSL_TLS (bool): Whether to use SSL/TLS for the mail server. Default is True.
        USE_CREDENTIALS (bool): Whether to use credentials for the mail server. Default is True.
        VALIDATE_CERTS (bool): Whether to validate certificates for the mail server. Default is True.
        TEMPLATE_FOLDER (Path): Path to the folder containing email templates.
        CLD_NAME (str): Cloud service name.
        CLD_API_KEY (int): API key for the cloud service.
        CLD_API_SECRET (str): API secret for the cloud service.
        model_config (ConfigDict): Configuration dictionary for the settings model.
    """

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = Path(__file__).parent.parent / "services" / "templates"

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
