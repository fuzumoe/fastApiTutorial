import os
from typing import TypeAlias

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

# Environment configuration
APP_NAME = os.getenv("APP_NAME", "Books Catalog API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple API to manage a books catalog")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Type alias for Book dictionary
Book: TypeAlias = dict[str, int | float | str | bool]

# Sample data
books: list[Book] = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "published": "2008-08-01",
        "pages": 464,
        "in_stock": True,
        "price": 35.99,
        "rating": 4.7,
    }
]

# Create FastAPI app
app = FastAPI(title=APP_NAME, description=APP_DESCRIPTION, version=APP_VERSION)


# 1. CREATE - POST /books
@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_books(
    book_data: Book | list[Book],
) -> Book | list[Book]:
    """
    Create one or multiple books.
    - Accepts either a single book object or a list of book objects
    - Assigns a unique ID to each book
    - Coerces types for numerical and boolean fields
    - Returns the created book(s)
    """
    # Handle both single book and list of books
    if isinstance(book_data, dict):
        # Single book
        new_book = process_book_data(book_data)
        books.append(new_book)
        return new_book
    else:
        # List of books
        new_books = []
        for book in book_data:
            new_book = process_book_data(book)
            books.append(new_book)
            new_books.append(new_book)
        return new_books


# 2. READ (Collection) - GET /books
@app.get("/books")
async def read_books(
    id: int | None = None,
    title: str | bytes | None = None,
    author: str | bytes | None = None,
    in_stock: bool | None = None,
    min_pages: int | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
) -> list[Book]:
    """
    Get all books with optional filtering.
    - Filters: id, title, author, in_stock (exact matches)
    - Range filters: min_pages (>=), max_price (<=), min_rating (>=)
    """
    filtered_books = books.copy()

    # Apply exact match filters
    if id is not None:
        filtered_books = [book for book in filtered_books if book["id"] == id]

    if title is not None:
        filtered_books = [book for book in filtered_books if book["title"] == title]

    if author is not None:
        filtered_books = [book for book in filtered_books if book["author"] == author]

    if in_stock is not None:
        filtered_books = [
            book for book in filtered_books if book["in_stock"] == in_stock
        ]

    # Apply range filters
    if min_pages is not None:
        filtered_books = [
            book for book in filtered_books if int(book["pages"]) >= min_pages
        ]

    if max_price is not None:
        filtered_books = [
            book for book in filtered_books if float(book["price"]) <= max_price
        ]

    if min_rating is not None:
        filtered_books = [
            book for book in filtered_books if float(book["rating"]) >= min_rating
        ]

    return filtered_books


# 3. READ (Single) - GET /books/{book_id}
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int) -> Book | None:
    """
    Get a single book by its ID.
    - Returns 404 if book not found
    """
    book: Book | None = find_book_by_id(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    return book


# 4. UPDATE (Partial) - PATCH /books/{book_id}
@app.patch("/books/{book_id}")
async def update_book_partial(book_id: int, book_data: Book) -> Book | None:
    """
    Update only the provided fields of a book.
    - Leaves unspecified fields unchanged
    - Coerces types when needed
    - Returns 404 if book not found
    """
    book_index = find_book_index(book_id)
    if book_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    # Get existing book
    current_book = books[book_index]

    # Apply updates (with type coercion where needed)
    for key, value in book_data.items():
        if key == "id":
            # Ignore ID changes
            continue
        if key == "pages":
            current_book[key] = int(value)
        elif key in ["price", "rating"]:
            current_book[key] = float(value)
        elif key == "in_stock":
            current_book[key] = bool(value)
        else:
            current_book[key] = value

    return current_book


# 5. UPDATE (Full Replace) - PUT /books/{book_id}
@app.put("/books/{book_id}")
async def update_book_full(book_id: int, book_data: Book) -> Book:
    """
    Replace all fields of a book.
    - Forces ID to remain unchanged
    - Coerces types for numerical and boolean fields
    - Returns 404 if book not found
    """
    book_index = find_book_index(book_id)
    if book_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    # Process the updated book data with type coercion
    updated_book = process_book_data(book_data, book_id)

    # Replace the book
    books[book_index] = updated_book

    return updated_book


# 6. DELETE - DELETE /books/{book_id}
@app.delete("/books/{book_id}")
async def delete_book(book_id: int) -> Book:
    """
    Delete a book by its ID.
    - Returns 404 if book not found
    - Returns a success message on successful deletion
    """
    book_index = find_book_index(book_id)
    if book_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    # Remove the book
    books.pop(book_index)

    return {"message": "Book deleted successfully"}


# 7. API Docs (Scalar)
@app.get("/scalar", response_class=HTMLResponse)
async def get_scalar_docs() -> str:
    """
    Serve Scalar API Reference UI.
    """
    return str(
        get_scalar_api_reference(
            app=app,
            title=f"{APP_NAME} API Reference",
            theme="dark",
        )
    )


# Helper functions
def process_book_data(data: Book, existing_id: int | None = None) -> Book:
    """
    Process book data with type coercion.
    - Assigns a new ID if not provided
    - Coerces types for numerical and boolean fields
    """
    # Determine the ID
    book_id = existing_id if existing_id is not None else get_next_id()

    # Create the book with proper type coercion
    book: Book = {
        "id": book_id,
        "title": data["title"],
        "author": data["author"],
        "published": data["published"],
        "pages": int(data["pages"]),
        "in_stock": bool(data["in_stock"]),
        "price": float(data["price"]),
        "rating": float(data["rating"]),
    }

    return book


def get_next_id() -> int:
    """Get the next available ID."""
    if not books:
        return 1
    return max(int(book["id"]) for book in books) + 1


def find_book_by_id(book_id: int) -> Book | None:
    """Find a book by its ID, return None if not found."""
    for book in books:
        if book["id"] == book_id:
            return book
    return None


def find_book_index(book_id: int) -> int:
    """Find the index of a book by its ID, return -1 if not found."""
    for i, book in enumerate(books):
        if book["id"] == book_id:
            return i
    return -1


# For direct execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
