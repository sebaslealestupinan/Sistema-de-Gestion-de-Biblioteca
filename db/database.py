from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from fastapi import Depends

url_database = "sqlite:///./databaseCatalogo.db"

engine = create_engine(
    url_database,
    echo=True,
    connect_args={"check_same_thread": False}
)

def create_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

sessionDep = Annotated[Session, Depends(get_session)]
