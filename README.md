# RESTful API Methods with FastAPI

This lesson introduces you to RESTful API methods using FastAPI. You'll learn how to implement the standard HTTP methods (GET, POST, PUT, PATCH, DELETE) to create a complete CRUD (Create, Read, Update, Delete) API for a Todo list application.

## What is REST?

REST (Representational State Transfer) is an architectural style for designing networked applications. RESTful APIs use standard HTTP methods to perform operations on resources, which are typically represented as JSON objects.

## HTTP Methods in REST

| Method | Purpose | Idempotent? | Safe? |
|--------|---------|-------------|-------|
| GET | Retrieve data | Yes | Yes |
| POST | Create data | No | No |
| PUT | Replace data | Yes | No |
| PATCH | Partially update data | Yes | No |
| DELETE | Remove data | Yes | No |

- **Idempotent**: Multiple identical requests have the same effect as a single request
- **Safe**: Does not modify resources (read-only)

## REST Implementation in FastAPI

### Basic Setup

Our FastAPI application is configured with environment variables for flexibility:

```python
import os
from typing import Any
from fastapi import FastAPI
import uvicorn

# Get environment variables with defaults
APP_NAME = os.getenv("APP_NAME", "FastAPI Tutorial")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple FastAPI application")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"
```

We've created a sample todos list to work with:

```python
todos = [
    {"id": 1, "task": "Learn FastAPI", "completed": False, "time": "2023-10-01T09:00:00", "priority": 1, "rate": 4.5},
    {"id": 2, "task": "Build a REST API", "completed": False, "time": "2023-10-02T10:00:00", "priority": 2, "rate": 3.8},
    {"id": 3, "task": "Deploy to production", "completed": False, "time": "2023-10-03T11:00:00", "priority": 3, "rate": 4.2},
]

# Create FastAPI instance
app = FastAPI(title=APP_NAME, description=APP_DESCRIPTION, version=APP_VERSION)
```

## Implementing REST Methods

### 1. POST Method - Creating Resources

The POST method is used to create new resources. In our example, it creates new todo items:

```python
@app.post("/todos")
async def create_todo(todo: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    if isinstance(todo, list):
        for item in todo:
            item["id"] = len(todos) + 1
            todos.append(item)
        return {"message": "Todos created successfully"}
    else:
        todo["id"] = len(todos) + 1
        todos.append(todo)
        return todo
```

**Key Features:**
- Accepts either a single todo item or a list of todos
- Automatically generates IDs for new items
- Returns the created todo or a success message

**Usage Example:**
```bash
# Create a single todo
curl -X POST "http://127.0.0.1:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"task": "Learn REST APIs", "completed": false, "priority": 1, "rate": 5.0}'
```

### 2. GET Method - Reading Resources

The GET method retrieves resources. It can retrieve all todos or filter them based on criteria:

```python
@app.get("/todos")
async def read_todos(filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if not filters:
        return todos
    filtered_todos = []
    for todo in todos:
        match = True
        for key, value in filters.items():
            if key in todo and todo[key] != value:
                match = False
                break
        if match:
            filtered_todos.append(todo)
    return filtered_todos
```

**Key Features:**
- Returns all todos when no filters are provided
- Supports filtering by any todo property
- Returns a list of matching todos

**Usage Example:**
```bash
# Get all todos
curl "http://127.0.0.1:8000/todos"

# Get todos filtered by completion status
curl "http://127.0.0.1:8000/todos?filters.completed=false"
```

We also have a method to get a single todo by ID:

```python
@app.post("/todos/{id}")
def get_todo(id: int) -> dict[str, Any] | None:
    for todo in todos:
        if todo["id"] == id:
            return todo
    return None
```

**Note:** This should actually be a GET method according to REST principles. We'll correct this issue later.

### 3. PATCH Method - Partially Updating Resources

The PATCH method is used for partial updates to a resource:

```python
@app.patch("/todos/{id}")
def update_todo(id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    todo = get_todo(id)
    if todo:
        todo.update(updates)
        return todo
    return None
```

**Key Features:**
- Updates only the specified fields
- Preserves other fields
- Returns the updated todo or None if not found

**Usage Example:**
```bash
# Update the completion status of a todo
curl -X PATCH "http://127.0.0.1:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### 4. PUT Method - Replacing Resources

The PUT method replaces an entire resource with a new version:

```python
@app.put("/todos/{id}")
def upudate_todo(id: int, todo: dict[str, Any]) -> dict[str, Any] | None:
    existing_todo = get_todo(id)
    if existing_todo:
        existing_todo.update(todo)
        return existing_todo
    return None
```

**Key Features:**
- Conceptually replaces the entire resource
- Returns the updated todo or None if not found

**Note:** In a true PUT implementation, if fields are not included in the request, they should be removed from the resource. Our implementation currently acts like PATCH.

**Usage Example:**
```bash
# Replace a todo completely
curl -X PUT "http://127.0.0.1:8000/todos/2" \
  -H "Content-Type: application/json" \
  -d '{"task": "Learn PUT vs PATCH", "completed": true, "priority": 2, "rate": 4.0, "time": "2023-10-05T15:00:00"}'
```

### 5. DELETE Method - Removing Resources

The DELETE method removes a resource:

```python
@app.delete("/todos/{id}")
def delete_todo(id: int) -> dict[str, str] | None:
    todo = get_todo(id)
    if todo:
        todos.remove(todo)
        return {"message": "Todo deleted successfully"}
    return None
```

**Key Features:**
- Removes the todo with the specified ID
- Returns a success message or None if not found

**Usage Example:**
```bash
# Delete a todo
curl -X DELETE "http://127.0.0.1:8000/todos/3"
```

## Best Practices and Improvements

Looking at our code, here are some improvements we could make:

1. **Fix the get_todo method**: It should use @app.get instead of @app.post:
```python
@app.get("/todos/{id}")  # Changed from post to get
def get_todo(id: int) -> dict[str, Any] | None:
    for todo in todos:
        if todo["id"] == id:
            return todo
    return None
```

2. **Implement proper PUT semantics**: Our PUT method should replace the entire resource:
```python
@app.put("/todos/{id}")
def replace_todo(id: int, new_todo: dict[str, Any]) -> dict[str, Any] | None:
    for i, todo in enumerate(todos):
        if todo["id"] == id:
            # Preserve the ID, but replace everything else
            new_todo["id"] = id
            todos[i] = new_todo
            return todos[i]
    return None
```

3. **Use Pydantic models**: Instead of using dict[str, Any], define proper Pydantic models:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    task: str
    completed: bool = False
    priority: int = Field(gt=0, lt=6)
    rate: float = Field(ge=0, le=5)

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    task: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, gt=0, lt=6)
    rate: Optional[float] = Field(None, ge=0, le=5)

class Todo(TodoBase):
    id: int
    time: datetime
```

4. **Add proper error handling**: Return appropriate status codes:
```python
from fastapi import HTTPException, status

@app.get("/todos/{id}")
def get_todo(id: int) -> Todo:
    for todo in todos:
        if todo["id"] == id:
            return todo
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo with id {id} not found"
    )
```

## The Pure Python Approach

In `examples/rest_methods.py`, we have implemented similar functionality without the web framework:

```python
def create_todo(task: str, priority: int, rate: float) -> dict[str, Any]:
    new_todo = {
        "id": len(todos) + 1,
        "task": task,
        "completed": False,
        "time": datetime.now().isoformat(),
        "priority": priority,
        "rate": rate,
    }
    todos.append(new_todo)
    return new_todo

def get_todos(filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    # Similar to the FastAPI implementation
    # ...

def patch_todo(todo_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    # Similar to the FastAPI implementation
    # ...

def update_todo(todo_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    # Similar to the FastAPI implementation
    # ...

def delete_todo(todo_id: int) -> bool:
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return True
```

This shows that REST principles can be implemented even in non-web contexts, as they simply represent operations on resources.

## REST Method Summary

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | /todos | create_todo | Create a new todo or batch of todos |
| GET | /todos | read_todos | Retrieve all todos (with optional filtering) |
| GET | /todos/{id} | get_todo | Retrieve a specific todo by ID |
| PATCH | /todos/{id} | update_todo | Partially update a todo |
| PUT | /todos/{id} | replace_todo | Replace a todo completely |
| DELETE | /todos/{id} | delete_todo | Remove a todo |

## Key Takeaways

1. **REST uses standard HTTP methods** to perform CRUD operations on resources
2. **GET** is for reading and should never modify data
3. **POST** creates new resources and generates IDs
4. **PUT** replaces resources completely
5. **PATCH** updates resources partially
6. **DELETE** removes resources
7. **Idempotent methods** (GET, PUT, PATCH, DELETE) can be safely retried
8. **URL paths** should identify resources, not actions

## Exercises

1. Add validation to ensure todos have required fields
2. Implement a search endpoint that finds todos by task name
3. Add a status code 201 (Created) to the POST method
4. Fix the get_todo method to use GET instead of POST
5. Improve the PUT implementation to truly replace resources

## Next Steps

In future lessons, we'll explore:
- Advanced request validation with Pydantic
- Authentication and authorization
- Database integration with SQLAlchemy
- API versioning
- Documentation with Swagger/OpenAPI
