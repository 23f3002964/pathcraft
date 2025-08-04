from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# We'll use a local SQLite database for this prototype
SQLALCHEMY_DATABASE_URL = "sqlite:///./pathcraft.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()