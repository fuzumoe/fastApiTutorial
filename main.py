import os
from fastapi import FastAPI
from pydantic import BaseModel
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


class CreateTodoRequest(BaseModel):
    task: str
    completed: bool
    time: str
    priority: int
    rate: float


class TodoResponse(BaseModel):
    id: int
    task: str
    completed: bool
    time: str
    priority: int
    rate: float


class TodoFilterRequest(BaseModel):
    task: str | None
    completed: bool | None
    time: str | None
    rate: float | None
    priority: int | None


class PatchTodoRequest(BaseModel):
    task: str | None
    completed: bool | None
    time: str | None
    priority: int | None
    rate: float | None


class UpdateTodoRequest(BaseModel):
    task: str
    completed: bool
    time: str
    priority: int
    rate: float


@app.post("/todos")
async def create_todo(
    todo: CreateTodoRequest | list[CreateTodoRequest]
) -> TodoResponse | list[TodoResponse]:
    if isinstance(todo, list):
        response = []
        for item in todo:
            item_dict = item.model_dump()
            item_dict["id"] = len(todos) + 1
            todos.append(item_dict)
            response.append(TodoResponse.model_validate(item_dict))
        return response
    else:
        todo_dict = todo.model_dump()
        todo_dict["id"] = len(todos) + 1
        todos.append(todo_dict)
        result: TodoResponse = TodoResponse.model_validate(todo_dict)
        return result


@app.get("/todos")
async def read_todos(filters: TodoFilterRequest | None = None) -> list[TodoResponse]:
    if not filters:
        return [TodoResponse.model_validate(todo) for todo in todos]

    filtered_todos = []
    # Only include non-None values in filter
    filter_dict = {k: v for k, v in filters.model_dump().items() if v is not None}

    for todo in todos:
        match = True
        for key, value in filter_dict.items():
            if key in todo and todo[key] != value:
                match = False
                break
        if match:
            filtered_todos.append(TodoResponse.model_validate(todo))

    return filtered_todos


@app.get("/todos/{id}")
def get_todo(id: int) -> TodoResponse | None:
    for todo in todos:
        if todo["id"] == id:
            result: TodoResponse = TodoResponse.model_validate(todo)
    return result


@app.patch("/todos/{id}")
def update_todo(id: int, updates: PatchTodoRequest) -> TodoResponse:
    for todo in todos:
        if todo["id"] == id:
            todo.update(updates.model_dump(exclude_unset=True))
            result: TodoResponse = TodoResponse.model_validate(todo)
    return result


@app.put("/todos/{id}")
def replace_todo_completely(id: int, todo: UpdateTodoRequest) -> TodoResponse:
    for existing_todo in todos:
        if existing_todo["id"] == id:
            existing_todo.update(todo.model_dump())
            result: TodoResponse = TodoResponse.model_validate(existing_todo)
    return result


@app.delete("/todos/{id}")
def delete_todo(id: int) -> dict[str, str] | None:
    for i, todo in enumerate(todos):
        if todo["id"] == id:
            todos.pop(i)
            return {"message": "Todo deleted successfully"}
    return None


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
