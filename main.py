import os
from typing import TypeAlias

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

# Get environment variables with defaults
APP_NAME = os.getenv("APP_NAME", "FastAPI Tutorial")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple FastAPI application")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"


Todo: TypeAlias = dict[str, int | float | str | bool]

todos: list[Todo] = [
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
async def crate_todo(
    payload: Todo | list[Todo],
) -> Todo | list[Todo]:
    if isinstance(payload, list):
        for item in payload:
            item["id"] = len(todos) + 1
            item["rate"] = float(item["rate"])
            todos.append(item)
    else:  # {}
        payload["id"] = len(todos) + 1
        payload["rate"] = float(payload["rate"])
        todos.append(payload)
    return payload


@app.get("/todos")
def read_todos(
    id: int | None = None,
    task: str | None = None,
    completed: bool | None = None,
    priority: int | None = None,
    rate: float | None = None,
    time: str | None = None,
) -> list[Todo]:
    filtered_todos = todos.copy()
    if id is not None:
        filtered_todos = [item for item in todos if item["id"] == id]
    if task is not None:
        filtered_todos = [item for item in todos if item["task"] == task]
    if completed is not None:
        filtered_todos = [item for item in todos if item["completed"] == completed]
    if priority is not None:
        filtered_todos = [item for item in todos if item["priority"] == priority]
    if rate is not None:
        filtered_todos = [item for item in todos if item["rate"] == rate]
    if time is not None:
        filtered_todos = [item for item in todos if item["time"] == time]

    return filtered_todos


@app.get("/todos/{id}")
def get_resource(id: int) -> Todo | None:
    for item in todos:
        if item["id"] == id:
            return item
    return None


@app.patch("/todos/{id}")
def partial_update(id: int, updates: Todo) -> Todo | None:
    result = None
    existing_todo = get_resource(id)
    if existing_todo:
        existing_todo.update(updates)
        result = get_resource(id)

    return result


@app.put("/todos/{id}")
def update(id: int, updates: Todo) -> Todo | None:
    result = None
    existing_todo = get_resource(id)
    if existing_todo:
        existing_todo.update(updates)
        result = get_resource(id)

    return result


@app.delete("/todos/{id}")
def delete_todo(id: int) -> dict[str, str] | None:
    existing_todo = get_resource(id)
    if existing_todo:
        todos.remove(existing_todo)
        return {"message": "Todo deleted successfully"}
    return None


@app.get("/scalar")
async def get_scalar() -> HTMLResponse:
    content: HTMLResponse = get_scalar_api_reference(
        openapi_url=app.openapi_url, title=APP_NAME
    )
    return content


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
