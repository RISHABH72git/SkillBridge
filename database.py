import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# Load from .env
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB")


MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Create engine with connection pool settings
engine = create_engine(
    MYSQL_URL,
    pool_size=5,  # max number of connections in pool
    max_overflow=10,  # extra connections beyond pool_size
    pool_timeout=30,  # wait (seconds) before giving up on getting a connection
    pool_recycle=1800,  # recycle connections after 30 min to avoid timeout
    pool_pre_ping=True  # check if connection is alive before using it
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()
