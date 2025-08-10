import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, cast

import motor.motor_asyncio
import uvicorn
from beanie import Document, init_beanie
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from scalar_fastapi import get_scalar_api_reference

logger = logging.getLogger(__name__)

# Get environment variables with defaults
# App
APP_NAME = os.getenv("APP_NAME", "FastAPI Tutorial")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple FastAPI application")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Api
API_DOCS_URL = os.getenv("API_DOCS_URL", "/docs")
REDOC_URL = os.getenv("REDOC_URL", "/redoc")
SCALARA_URL = os.getenv("SCALARA_URL", "/scalar")
OPENAPI_URL = os.getenv("OPENAPI_URL", "/openapi.json")

# Database
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27019"))
MONGO_DB = os.getenv("MONGO_DB", "fastapi_tutorial")
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "example")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_AUTH_SOURCE}"

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


class Todo(Document):
    task: str
    completed: bool
    time: datetime
    priority: int
    rate: float

    class Settings:
        name = "todos"


async def init(app: FastAPI) -> None:
    client: motor.motor_asyncio.AsyncIOMotorClient = (
        motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    )
    app.state.mongo_client = client
    db = client[MONGO_DB]
    await init_beanie(database=cast(Any, db), document_models=[Todo])


async def remove_all_data() -> None:
    logger.info("Removing all todos...")
    await Todo.delete_all()
    logger.info("All todos removed.")


async def populate_data() -> None:
    logger.info("No todos found, populating initial data...")
    initial_todos = []
    for todo_data in todos:
        todo_dict = dict(todo_data)
        todo_dict.pop("id", None)
        initial_todos.append(Todo(**todo_dict))

    await Todo.insert_many(initial_todos)
    logger.info("Initial data populated.")


# lifecycle events trigger init at startup
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.info("Starting FastAPI application...")
        await init(app)
        await remove_all_data()
        await populate_data()
        yield
        logger.info("Shutting down FastAPI application...")
        if hasattr(app.state, "mongo_client") and app.state.mongo_client is not None:
            try:
                app.state.mongo_client.close()
            except Exception as e:
                logger.error(f"Error closing MongoDB client: {e}")
    except Exception as e:
        logger.error(f"Error in lifespan: {e}", exc_info=True)
        yield


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url=API_DOCS_URL,
    openapi_url=OPENAPI_URL,
    redoc_url=REDOC_URL,
    scalar_url=SCALARA_URL,
    lifespan=lifespan,
)


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
    todo: CreateTodoRequest | list[CreateTodoRequest],
) -> TodoResponse | list[TodoResponse]:
    logger.info("Creating new todo(s)")

    if isinstance(todo, list):
        logger.debug(f"Creating batch of {len(todo)} todos")
        todo_objects = [Todo(**item.model_dump()) for item in todo]
        await Todo.insert_many(todo_objects)

        # create stable 1-based ids based on insertion order
        response: list[TodoResponse] = []
        # fetch all to ensure order (you could also rely on todo_objects order)
        all_todos = await Todo.find_all().to_list()
        id_map = {str(t.id): i + 1 for i, t in enumerate(all_todos)}
        for t in todo_objects:
            td = t.model_dump()
            td["id"] = id_map.get(str(t.id), 0)
            response.append(TodoResponse(**td))

        logger.info(f"Successfully created {len(response)} todos")
        return response

    logger.debug(f"Creating single todo: {todo.task}")
    todo_obj = Todo(**todo.model_dump())
    await todo_obj.insert()

    # compute 1-based id by current ordering
    all_todos = await Todo.find_all().to_list()
    idx = next(
        (i for i, t in enumerate(all_todos) if str(t.id) == str(todo_obj.id)),
        len(all_todos) - 1,
    )
    result_dict = todo_obj.model_dump()
    result_dict["id"] = idx + 1
    result = TodoResponse(**result_dict)

    logger.info(f"Successfully created todo with id {result.id}")
    return result


@app.get("/todos")
async def read_todos(filters: TodoFilterRequest | None = None) -> list[TodoResponse]:
    if not filters:
        logger.info("Fetching all todos")
        all_todos = await Todo.find_all().to_list()
        response: list[TodoResponse] = []
        for i, todo in enumerate(all_todos):
            td = todo.model_dump()
            td["id"] = i + 1
            response.append(TodoResponse(**td))
        return response

    filter_dict = {k: v for k, v in filters.model_dump().items() if v is not None}
    logger.info(f"Fetching todos with filters: {filter_dict}")

    filtered_todos = await Todo.find(filter_dict).to_list()

    all_todos = await Todo.find_all().to_list()
    id_map = {str(todo.id): i + 1 for i, todo in enumerate(all_todos)}

    filtered_response: list[TodoResponse] = []
    for todo in filtered_todos:
        td = todo.model_dump()
        td["id"] = id_map.get(str(todo.id), 0)
        filtered_response.append(TodoResponse(**td))

    logger.info(f"Found {len(filtered_response)} todos matching filters")
    return filtered_response


@app.get("/todos/{id}")
async def get_todo(id: int) -> TodoResponse | None:
    logger.info(f"Fetching todo with id {id}")
    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        td = todo.model_dump()
        td["id"] = id
        result = TodoResponse(**td)
        logger.info(f"Found todo with id {id}")
        return result
    logger.warning(f"Todo with id {id} not found")
    return None


@app.patch("/todos/{id}")
async def update_todo(id: int, updates: PatchTodoRequest) -> TodoResponse | None:
    logger.info(f"Partially updating todo with id {id}")
    update_fields = updates.model_dump(exclude_unset=True)

    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        for field, value in update_fields.items():
            setattr(todo, field, value)
        await todo.save()

        td = todo.model_dump()
        td["id"] = id
        result = TodoResponse(**td)
        logger.info(f"Successfully updated todo with id {id}")
        return result

    logger.warning(f"Todo with id {id} not found for update")
    return None


@app.put("/todos/{id}")
async def replace_todo_completely(
    id: int, todo_data: UpdateTodoRequest
) -> TodoResponse | None:
    logger.info(f"Completely replacing todo with id {id}")

    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        for field, value in todo_data.model_dump().items():
            setattr(todo, field, value)
        await todo.save()

        rd = todo.model_dump()
        rd["id"] = id
        result = TodoResponse(**rd)
        logger.info(f"Successfully replaced todo with id {id}")
        return result

    logger.warning(f"Todo with id {id} not found for replacement")
    return None


@app.delete("/todos/{id}")
async def delete_todo(id: int) -> dict[str, str] | None:
    logger.info(f"Deleting todo with id {id}")
    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        await todo.delete()
        logger.info(f"Successfully deleted todo with id {id}")
        return {"message": "Todo deleted successfully"}
    logger.warning(f"Todo with id {id} not found for deletion")
    return None


@app.get("/scalar")
async def get_scalar() -> HTMLResponse:
    content: HTMLResponse = get_scalar_api_reference(
        openapi_url=app.openapi_url, title=APP_NAME
    )
    return content


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
