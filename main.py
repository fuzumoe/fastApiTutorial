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


todos = [
    {
        "id": 1,
        "task": "Learn FastAPI",
        "completed": False,
        "time": "2023-10-01T09:00:00",
        "priority": 1,
        "rate": 4.5,
    },
    {
        "id": 2,
        "task": "Build a REST API",
        "completed": False,
        "time": "2023-10-02T10:00:00",
        "priority": 2,
        "rate": 3.8,
    },
    {
        "id": 3,
        "task": "Deploy to production",
        "completed": False,
        "time": "2023-10-03T11:00:00",
        "priority": 3,
        "rate": 4.2,
    },
]
# Create FastAPI instance
app = FastAPI(title=APP_NAME, description=APP_DESCRIPTION, version=APP_VERSION)


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


@app.post("/todos/{id}")
def get_todo(id: int) -> dict[str, Any] | None:
    for todo in todos:
        if todo["id"] == id:
            return dict(todo)  # Explicitly return as dict
    return None


@app.patch("/todos/{id}")
def update_todo(id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    todo = get_todo(id)
    if todo:
        todo.update(updates)
        return dict(todo)  # Explicitly return as dict
    return None


@app.put("/todos/{id}")
def upudate_todo(id: int, todo: dict[str, Any]) -> dict[str, Any] | None:
    existing_todo = get_todo(id)
    if existing_todo:
        existing_todo.update(todo)
        return dict(existing_todo)  # Explicitly return as dict
    return None


@app.delete("/todos/{id}")
def delete_todo(id: int) -> dict[str, str] | None:
    todo = get_todo(id)
    if todo:
        todos.remove(todo)
        return {"message": "Todo deleted successfully"}
    return None


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
