import os
from dotenv import load_dotenv

load_dotenv()


def get_required_env(name: str) -> str:
    """Get a required environment variable."""
    value = os.getenv(name)

    if not value or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


class Config:
    """Base configuration."""
    JWT_SECRET = get_required_env("JWT_SECRET")
    DATABASE = os.getenv("DATABASE")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"


class DevelopmentConfig(Config):
    """Development configuration."""
    pass


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True


class ProductionConfig(Config):
    """Production configuration."""
    pass