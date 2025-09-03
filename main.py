from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from enum import Enum
from typing import Any, cast

import uvicorn
from beanie import Document, Insert, Link, before_event, init_beanie
from fastapi import FastAPI, status
from fastapi.concurrency import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from app.core.config import app_settings, database_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ActionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Book(Document):
    title: str
    author: str
    published: str
    pages: int
    in_stock: bool
    price: float
    rating: float

    class Settings:
        name = "books"


class Activities(Document):
    todo: Link[Book]
    action_type: ActionType
    details: str | None
    timestamp: datetime

    @before_event(Insert)
    def set_timestamp(self) -> None:
        self.timestamp = datetime.now(tz=UTC)

    class Settings:
        name = "activities"


class PartialBookResponse(BaseModel):
    id: int | None = None
    title: str | None = None
    author: str | None = None
    published: str | None = None
    pages: int | None = None
    in_stock: bool | None = None
    price: float | None = None
    rating: float | None = None


class BookOpResponse(BaseModel):
    success: bool
    message: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting up...")
    client: AsyncIOMotorClient = AsyncIOMotorClient(database_settings.connection_url)
    db = client.get_default_database()
    logger.info("Initializing Beanie ODM...")
    await init_beanie(database=cast(Any, db), document_models=[Book])
    logger.info("Beanie ODM initialized.")
    yield
    # Shutdown
    logger.info("Shutting down...")
    client.close()


# Create FastApi app
app = FastAPI(
    title=app_settings.name,
    description=app_settings.description,
    version=app_settings.version,
    lifespan=lifespan,
)


@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(
    book_data: Book | list[Book],
) -> Book | list[Book] | None:
    """Create book endpoint"""
    logger.debug(f"Creating book: {book_data}")
    if isinstance(book_data, list):
        await Book.insert_many(book_data)
        return book_data
    logger.debug(f"Saving book: {book_data}")
    await book_data.save()  # or book_data.create can be used
    return book_data


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_book(
    id: int | None = None,
    title: str | None = None,
    author: str | None = None,
    published: str | None = None,
    pages: int | None = None,
    in_stock: bool | None = None,
    price: float | None = None,
    rating: float | None = None,
) -> Book | list[Book] | None:
    """Get books by filter"""
    logger.debug("Reading books with filters")
    return None


@app.put("/books/{book_id}", status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book_data: Book) -> BookOpResponse | None:
    """Update book by id"""
    logger.debug(f"Updating book {book_id}: {book_data}")
    return None


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int) -> None:
    """Delete book"""
    logger.debug(f"Deleting book {book_id}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.reload,
    )
