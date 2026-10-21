import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_required_env(name: str) -> str:
    """Get a required environment variable."""
    value = os.getenv(name)

    if not value or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def sqlite_uri(path):
    """Build an absolute SQLite database URI."""
    return f"sqlite:///{Path(path).resolve().as_posix()}"


class Config:
    """Base configuration."""
    JWT_SECRET = get_required_env("JWT_SECRET")
    DATABASE = os.getenv("DATABASE", "recipes.db")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = sqlite_uri(
        PROJECT_ROOT / Config.DATABASE
    )


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE = "instance/test_recipes.db"
    SQLALCHEMY_DATABASE_URI = sqlite_uri(
        PROJECT_ROOT / DATABASE
    )


class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = sqlite_uri(
        PROJECT_ROOT / Config.DATABASE
    )