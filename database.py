from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./strings.db"

# Create the engine
engine = create_engine( # Connects the app to the SQLite database file (string.db)
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Creates a session for interacting with the database.

# Base class for models
Base = declarative_base() # Parent class that the models will inherit from.