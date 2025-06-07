"""Configuration settings module for the application."""

import secrets
import warnings
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_core(value: Any) -> list[str] | str:
    """
    Parses CORS origins from a string or list.
    
    If given a comma-separated string, returns a list of trimmed origins. If given a list or a string starting with '[', returns the value as is. Raises a ValueError for invalid input types.
    
    Args:
        value: A string or list representing CORS origins.
    
    Returns:
        A list of origin strings or the original string.
    
    Raises:
        ValueError: If the input is not a valid string or list format.
    """
    if isinstance(value, str) and not value.startswith("["):
        return [i.strip() for i in value.split(",")]
    elif isinstance(value, list | str):
        return value
    raise ValueError(f"Invalid value for BACKEND_CORS_ORIGINS: {value}")


"""Settings for the application."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_URL: str = "http://localhost:5175"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_core)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Returns all allowed CORS origins as a list of strings.
        
        Includes all backend CORS origins with trailing slashes removed, plus the frontend URL.
        """
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_URL
        ]

    PROJECT_NAME: str = "Batchcooking AI API"
    SENTRY_DSN: str | None = None

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Constructs the SQLAlchemy database URI for the configured PostgreSQL server.
        
        Returns:
            The PostgreSQL DSN as a SQLAlchemy-compatible URI using the current settings.
        """
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI_LOCAL(self) -> PostgresDsn:
        """
        Constructs a SQLAlchemy-compatible PostgreSQL URI for a local database connection.
        
        Returns:
            A PostgreSQL DSN using the configured database name, user, and password, with host set to "localhost" and port 5436.
        """
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host="localhost",
            port= 5436,
            path=f"{self.POSTGRES_DB}",
        )
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        """
        Sets the default sender name for emails to the project name if not explicitly provided.
        """
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """
        Indicates whether email sending is enabled based on SMTP host and sender email configuration.
        
        Returns:
            True if both SMTP host and sender email are set; otherwise, False.
        """
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """
        Checks if a secret configuration value is set to the insecure default "changethis".
        
        If the value is "changethis" and the environment is "local", a warning is issued.
        In other environments, a ValueError is raised to enforce secure configuration.
        """
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """
        Ensures that sensitive secrets are not set to insecure default values.
        
        After model initialization, checks that `SECRET_KEY`, `POSTGRES_PASSWORD`, and `FIRST_SUPERUSER_PASSWORD` are not set to "changethis". Issues a warning in the "local" environment or raises a `ValueError` otherwise.
        """
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore
