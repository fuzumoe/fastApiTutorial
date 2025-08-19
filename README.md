# 📚 FastAPI CRUD Exercise — Books Catalog (Assignment Sheet)

Design and complete a small **FastAPI** application that manages a **Books Catalog** (in memory). This assignment mirrors a typical REST API you’d build in practice and is aligned with your Todos example.

> You already have a starter `main_books.py` (with TODOs). Your goal is to implement **Create**, **Read**, **Update**, and **Delete** endpoints exactly as specified below, plus basic filters and an API docs page via Scalar.

---
## 🚀 Environment Setup

Before starting the assignment, set up your Python environment:

### Virtual Environment
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# Install required packages
uv add fastapi uvicorn scalar-fastapi
```
---
## 🧩 Data Model

Each **Book** is a dictionary with these fields:

| Field       | Type   | Example                     | Notes                                           |
|-------------|--------|-----------------------------|-------------------------------------------------|
| `id`        | int    | `1`                         | Unique identifier (assigned by server)          |
| `title`     | str    | `"Clean Architecture"`      | Title of the book                               |
| `author`    | str    | `"Robert C. Martin"`        | Author name                                     |
| `published` | str    | `"2017-09-20"`              | ISO date string (YYYY-MM-DD)                    |
| `pages`     | int    | `432`                       | Coerce to `int` when creating/updating          |
| `in_stock`  | bool   | `true`                      | Coerce to `bool` when creating/updating         |
| `price`     | float  | `29.99`                     | Coerce to `float` when creating/updating        |
| `rating`    | float  | `4.7`                       | Coerce to `float` (range 0–5 not enforced here) |

IDs are **server-assigned** (incremental). Storage is **in-memory** (a Python list), no database.

---

## 🎯 Tasks (What You Must Implement)

### 1) CREATE — `POST /books`
**Goal:** Create **one** book or **many** books in a single request.

**Requirements**
- Accept either a single JSON object or a list of JSON objects.
- For each book:
  - Assign a unique `id` on the server.
  - Coerce `pages` → `int`, `price` → `float`, `rating` → `float`, `in_stock` → `bool`.
- Return the created book(s) as JSON.

**Examples**
```bash
# Create one
curl -s -X POST http://127.0.0.1:8000/books   -H "Content-Type: application/json"   -d '{"title":"Python Tricks","author":"Dan Bader","published":"2017-10-01","pages":302,"in_stock":true,"price":24.99,"rating":4.5}' | jq

# Create many
curl -s -X POST http://127.0.0.1:8000/books   -H "Content-Type: application/json"   -d '[{"title":"Pragmatic Programmer","author":"Hunt & Thomas","published":"1999-10-30","pages":352,"in_stock":true,"price":31.99,"rating":4.7},
       {"title":"Effective Python","author":"Brett Slatkin","published":"2015-03-01","pages":256,"in_stock":false,"price":27.99,"rating":4.6}]' | jq
```

---

### 2) READ (Collection) — `GET /books`
**Goal:** List books with optional filtering.

**Filters (all optional)**
- Exact matches: `id`, `title`, `author`, `in_stock`
- Ranged filters: `min_pages` (>=), `max_price` (<=), `min_rating` (>=)

**Examples**
```bash
# List all
curl -s http://127.0.0.1:8000/books | jq

# In-stock books under $35, rating at least 4.5
curl -s "http://127.0.0.1:8000/books?in_stock=true&max_price=35&min_rating=4.5" | jq

# Books with at least 500 pages
curl -s "http://127.0.0.1:8000/books?min_pages=500" | jq
```

---

### 3) READ (Single) — `GET /books/{book_id}`
**Goal:** Return a single book by its `id`.

**Requirements**
- If the book exists, return it (200).
- If not, return `404 Not Found`.

**Example**
```bash
curl -s http://127.0.0.1:8000/books/2 | jq
```

---

### 4) UPDATE (Partial) — `PATCH /books/{book_id}`
**Goal:** Update **only** the fields provided.

**Requirements**
- If book not found → `404`.
- Coerce types for any of: `pages`, `price`, `rating`, `in_stock` **when present**.
- Leave unspecified fields unchanged.
- Return the updated book.

**Example**
```bash
# Update only the price
curl -s -X PATCH http://127.0.0.1:8000/books/1   -H "Content-Type: application/json"   -d '{"price":27.49}' | jq
```

---

### 5) UPDATE (Full Replace) — `PUT /books/{book_id}`
**Goal:** Replace **all** fields for a book.

**Requirements**
- If book not found → `404`.
- Force `id` to remain `book_id`.
- Coerce `pages`, `price`, `rating`, `in_stock`.
- Return the replaced book.

**Example**
```bash
curl -s -X PUT http://127.0.0.1:8000/books/2   -H "Content-Type: application/json"   -d '{"title":"DDIA (2nd Ed.)","author":"Martin Kleppmann","published":"2024-01-01","pages":700,"in_stock":false,"price":44.95,"rating":4.9}' | jq
```

---

### 6) DELETE — `DELETE /books/{book_id}`
**Goal:** Remove a book.

**Requirements**
- If book not found → `404`.
- On success, return `{"message": "Book deleted successfully"}`.

**Example**
```bash
curl -s -X DELETE http://127.0.0.1:8000/books/3 | jq
```

---

### 7) API Docs (Scalar)
**Goal:** Serve a human-friendly API reference.

**Requirements**
- Provide `GET /scalar` that returns Scalar’s API Reference UI using your app’s OpenAPI schema.
- After running, open: `http://127.0.0.1:8000/scalar`

---

## 🧪 How to Run & Test

```bash
uvicorn main_books:app --reload
# Open docs:
# http://127.0.0.1:8000/scalar
```

Run the **Examples** shown in each section to verify behavior.

---

## ✅ Acceptance Checklist (Grading)

- [ ] **Create (POST /books)** supports single & bulk create, assigns `id`, coerces types, returns created data.
- [ ] **Read (GET /books)** returns all books and supports all listed filters (exact + ranged).
- [ ] **Read (GET /books/{id})** returns the correct book or `404`.
- [ ] **Patch (PATCH /books/{id})** updates only provided fields, coerces types, or returns `404`.
- [ ] **Put (PUT /books/{id})** fully replaces a book, preserves `id`, coerces types, or returns `404`.
- [ ] **Delete (DELETE /books/{id})** removes a book or returns `404`.
- [ ] **Scalar UI** is available at `/scalar`.
- [ ] Code runs without runtime errors and behaves as specified.

---
## 🧠 Hints

 ```python
import os
from typing import TypeAlias, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

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
        "rating": 4.7
    }
]
```
