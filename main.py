import logging
import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from enum import Enum
from typing import Any, cast

import motor.motor_asyncio
import uvicorn
from beanie import Document, Insert, Link, before_event, init_beanie
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from scalar_fastapi import get_scalar_api_reference

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("all_logs.log", mode="a"),
    ],
)
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
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "27019"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "mydb")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "example")
DATABASE_AUTH_SOURCE = os.getenv("DATABASE_AUTH_SOURCE", "admin")
MONGO_URI = f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?authSource={DATABASE_AUTH_SOURCE}"


class ActionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Todo(Document):
    task: str
    completed: bool
    time: datetime
    priority: int
    rate: float

    class Settings:
        name = "todos"


class Activities(Document):
    todo: Link[Todo]
    action_type: ActionType
    details: str | None
    timestamp: datetime

    @before_event(Insert)
    def set_timestamp(self) -> None:
        self.timestamp = datetime.now(tz=UTC)

    class Settings:
        name = "activities"


async def initialize_database(app: FastAPI) -> None:
    logger.info("Starting database initialization...")
    try:
        client: motor.motor_asyncio.AsyncIOMotorClient = (
            motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        )
        logger.info(f"Connecting to MongoDB at {DATABASE_HOST}:{DATABASE_PORT}...")
        await client.admin.command("ping")
        logger.info("MongoDB connection successful!")
        app.state.mongo_client = client
        db = client[DATABASE_NAME]
        logger.info(f"Initializing Beanie with database: {DATABASE_NAME}")
        await init_beanie(database=cast(Any, db), document_models=[Todo, Activities])
        logger.info("Database initialization complete!")

        # Ensure collections exist by creating and possibly removing sample data
        await seed_sample_data()
        logger.info("Collections verified!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e!s}", exc_info=True)
        raise


async def remove_all_data() -> None:
    logger.info("Removing all todos...")
    await Todo.delete_all()
    logger.info("All todos removed.")


async def seed_sample_data() -> None:
    """Create sample data if collections don't exist yet."""
    logger.info("Checking if collections exist...")

    # Get the database directly
    client: motor.motor_asyncio.AsyncIOMotorClient = (
        motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    )
    db = client[DATABASE_NAME]
    collections = await db.list_collection_names()

    if "todos" not in collections or "activities" not in collections:
        logger.info("Collections don't exist. Creating sample data...")
        # Create a sample todo
        sample_todo = Todo(
            task="Sample task created on startup",
            completed=False,
            time=datetime.now(tz=UTC),
            priority=1,
            rate=5.0,
        )
        await sample_todo.save()
        logger.info(f"Created sample todo: {sample_todo.task}")

        # Create a sample activity
        sample_activity = Activities(
            todo=sample_todo,
            action_type=ActionType.CREATE,
            details="Sample activity created on startup",
            timestamp=datetime.now(tz=UTC),  # Set timestamp explicitly
        )
        await sample_activity.save()
        logger.info("Created sample activity")

        # Now remove the sample data (optional - remove this if you want to keep the samples)
        await sample_todo.delete()
        await sample_activity.delete()
        logger.info("Removed sample data after collection creation")
    else:
        logger.info(f"Collections already exist: {collections}")

    # Close the client
    client.close()


async def create_todo_event(todo: Todo | list[Todo]) -> None:
    logger.info("Handling todo creation event")
    current_time = datetime.now(tz=UTC)

    if isinstance(todo, list):
        # We can use insert_many here because all todos now have IDs
        # (they were saved individually in create_todo_service)
        activities = [
            Activities(
                todo=t,
                action_type=ActionType.CREATE,
                details=f"Todo created: {t.task}",
                timestamp=current_time,
            )
            for t in todo
        ]
        await Activities.insert_many(activities)  # Batch insert activities
        for t in todo:
            logger.info(f"Todo created: {t.task}")
        logger.info(f"Successfully created {len(activities)} activities")
        return

    logger.info(f"Todo created: {todo.task}")
    activity = Activities(
        todo=todo,
        action_type=ActionType.CREATE,
        details=f"Todo created: {todo.task}",
        timestamp=current_time,
    )
    await activity.save()
    logger.info("Todo creation event handled successfully")


async def update_todo_event(todo: Todo) -> None:
    logger.info(f"Todo updated: {todo.task}")
    activity = Activities(
        todo=todo,
        action_type=ActionType.UPDATE,
        details=f"Todo updated: {todo.task}",
        timestamp=datetime.now(tz=UTC),
    )
    await activity.save()


async def delete_todo_event(todo: Todo) -> None:
    logger.info(f"Todo deleted: {todo.task}")
    activity = Activities(
        todo=todo,
        action_type=ActionType.DELETE,
        details=f"Todo deleted: {todo.task}",
        timestamp=datetime.now(tz=UTC),
    )
    await activity.save()


# lifecycle events trigger init at startup
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Lifespan context manager triggered")
    try:
        logger.info("Starting FastAPI application...")
        logger.info("Initializing database from lifespan...")
        await initialize_database(app)
        logger.info("Application startup complete")
        yield
        logger.info("Shutting down FastAPI application...")
        if hasattr(app.state, "mongo_client") and app.state.mongo_client is not None:
            try:
                logger.info("Closing MongoDB connection...")
                app.state.mongo_client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB client: {e!s}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in lifespan: {e!s}", exc_info=True)
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
    time: datetime | None
    priority: int
    rate: float


class TodoResponse(BaseModel):
    id: int
    task: str
    completed: bool
    time: str  # Changed from datetime to str for ISO format strings
    priority: int
    rate: float


class TodoFilterRequest(BaseModel):
    task: str | None
    completed: bool | None
    time: datetime | None
    rate: float | None
    priority: int | None


class PatchTodoRequest(BaseModel):
    task: str | None
    completed: bool | None
    time: datetime | None
    priority: int | None
    rate: float | None


class UpdateTodoRequest(BaseModel):
    task: str
    completed: bool
    time: datetime
    priority: int
    rate: float


async def create_todo_service(
    todo_data: CreateTodoRequest | list[CreateTodoRequest],
    background_tasks: BackgroundTasks,
) -> TodoResponse | list[TodoResponse] | None:
    logger.info("Creating new todo")

    if isinstance(todo_data, list):
        # Save todos one by one to ensure each has an ID before the event is triggered
        todos = []
        for item in todo_data:
            todo = Todo(**item.model_dump())
            await todo.save()  # Save individually to get IDs
            todos.append(todo)
        background_tasks.add_task(create_todo_event, todos)
        logger.info("Successfully created new todos")

        responses = []
        for i, todo in enumerate(todos):
            td = todo.model_dump()
            td["id"] = i + 1  # Convert to integer ID
            if isinstance(td["time"], datetime):
                td["time"] = td["time"].isoformat()  # Convert datetime to string
            responses.append(TodoResponse(**td))
        return responses
    else:
        todo = Todo(**todo_data.model_dump())
        await todo.save()
        background_tasks.add_task(create_todo_event, todo)
        logger.info("Successfully created new todo")

        td = todo.model_dump()
        td["id"] = 1  # Use a simple ID
        if isinstance(td["time"], datetime):
            td["time"] = td["time"].isoformat()  # Convert datetime to string
        return TodoResponse(**td)


async def read_todos_service(
    filters: TodoFilterRequest | None = None,
) -> list[TodoResponse]:
    if not filters:
        logger.info("Fetching all todos")
        all_todos = await Todo.find_all().to_list()
        response: list[TodoResponse] = []
        for i, todo in enumerate(all_todos):
            td = todo.model_dump()
            td["id"] = i + 1  # Convert to integer ID
            if isinstance(td["time"], datetime):
                td["time"] = td["time"].isoformat()  # Convert datetime to string
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
        td["id"] = id_map.get(str(todo.id), 0)  # Convert to integer ID
        if isinstance(td["time"], datetime):
            td["time"] = td["time"].isoformat()  # Convert datetime to string
        filtered_response.append(TodoResponse(**td))

    logger.info(f"Found {len(filtered_response)} todos matching filters")
    return filtered_response


async def get_todo_service(id: int) -> TodoResponse | None:
    logger.info(f"Fetching todo with id {id}")
    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        td = todo.model_dump()
        td["id"] = id  # Keep the integer ID
        if isinstance(td["time"], datetime):
            td["time"] = td["time"].isoformat()  # Convert datetime to string
        result = TodoResponse(**td)
        logger.info(f"Found todo with id {id}")
        return result
    logger.warning(f"Todo with id {id} not found")
    return None


async def update_todo_service(
    id: int, updates: PatchTodoRequest, background_tasks: BackgroundTasks
) -> TodoResponse | None:
    logger.info(f"Partially updating todo with id {id}")
    update_fields = updates.model_dump(exclude_unset=True)

    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        for field, value in update_fields.items():
            setattr(todo, field, value)
        background_tasks.add_task(update_todo_event, todo)
        await todo.save()

        td = todo.model_dump()
        td["id"] = id  # Keep the integer ID
        if isinstance(td["time"], datetime):
            td["time"] = td["time"].isoformat()  # Convert datetime to string
        result = TodoResponse(**td)
        logger.info(f"Successfully updated todo with id {id}")
        return result

    logger.warning(f"Todo with id {id} not found for update")
    return None


async def replace_todo_service(
    id: int, todo_data: UpdateTodoRequest, background_tasks: BackgroundTasks
) -> TodoResponse | None:
    logger.info(f"Completely replacing todo with id {id}")

    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        for field, value in todo_data.model_dump().items():
            setattr(todo, field, value)
        background_tasks.add_task(update_todo_event, todo)
        await todo.save()

        rd = todo.model_dump()
        rd["id"] = id  # Keep the integer ID
        if isinstance(rd["time"], datetime):
            rd["time"] = rd["time"].isoformat()  # Convert datetime to string
        result = TodoResponse(**rd)
        logger.info(f"Successfully replaced todo with id {id}")
        return result

    logger.warning(f"Todo with id {id} not found for replacement")
    return None


async def delete_todo_service(
    id: int, background_tasks: BackgroundTasks
) -> dict[str, str] | None:
    logger.info(f"Deleting todo with id {id}")
    all_todos = await Todo.find_all().to_list()
    if 0 < id <= len(all_todos):
        todo = all_todos[id - 1]
        await todo.delete()
        background_tasks.add_task(delete_todo_event, todo)
        logger.info(f"Successfully deleted todo with id {id}")
        return {"message": "Todo deleted successfully"}
    logger.warning(f"Todo with id {id} not found for deletion")
    return None


@app.post("/todos", status_code=201)
async def create_todo(
    todo: CreateTodoRequest | list[CreateTodoRequest], background_tasks: BackgroundTasks
) -> TodoResponse | list[TodoResponse] | None:
    return await create_todo_service(todo, background_tasks)


@app.get("/todos")
async def read_todos(
    filters: TodoFilterRequest | None = None,
) -> list[TodoResponse]:
    return await read_todos_service(filters)


@app.patch("/todos/{id}")
async def update_todo(
    id: int, updates: PatchTodoRequest, background_tasks: BackgroundTasks
) -> TodoResponse | None:
    return await update_todo_service(id, updates, background_tasks)


@app.get("/todos/{id}")
async def read_todo(id: int) -> TodoResponse | None:
    return await get_todo_service(id)


@app.put("/todos/{id}")
async def replace_todo(
    id: int, todo_data: UpdateTodoRequest, background_tasks: BackgroundTasks
) -> TodoResponse | None:
    return await replace_todo_service(id, todo_data, background_tasks)


@app.delete("/todos/{id}")
async def delete_todo(
    id: int, background_tasks: BackgroundTasks
) -> dict[str, str] | None:
    return await delete_todo_service(id, background_tasks)


@app.get("/scalar")
async def get_scalar() -> HTMLResponse:
    content: HTMLResponse = get_scalar_api_reference(
        openapi_url=app.openapi_url, title=APP_NAME
    )
    return content


@app.get("/db-status")
async def db_status() -> dict[str, Any]:
    """Check database connection status and return info about collections."""
    try:
        # Check if client exists
        if not hasattr(app.state, "mongo_client") or app.state.mongo_client is None:
            return {
                "status": "Not connected",
                "error": "MongoDB client not initialized",
            }

        # Check connection
        await app.state.mongo_client.admin.command("ping")

        # Get collection info
        db = app.state.mongo_client[DATABASE_NAME]
        collections = await db.list_collection_names()

        # Get document counts
        collection_counts = {}
        for coll in collections:
            count = await db[coll].count_documents({})
            collection_counts[coll] = count

        return {
            "status": "Connected",
            "database": DATABASE_NAME,
            "collections": collections,
            "collection_counts": collection_counts,
        }
    except Exception as e:
        logger.error(f"Error checking database status: {e}", exc_info=True)
        return {"status": "Error", "error": str(e)}


@app.post("/create-test-todo")
async def create_test_todo(background_tasks: BackgroundTasks) -> TodoResponse:
    """Create a test todo to verify database connection and model conversions."""
    test_todo = CreateTodoRequest(
        task="Test todo created via endpoint",
        completed=False,
        time=datetime.now(tz=UTC),
        priority=1,
        rate=5.0,
    )
    result = await create_todo_service(test_todo, background_tasks)
    if result is None:
        # Fallback if something went wrong
        return TodoResponse(
            id=0,
            task="Failed to create todo",
            completed=False,
            time=datetime.now(tz=UTC).isoformat(),
            priority=0,
            rate=0.0,
        )
    # We know it's a single response and not a list or None
    return cast(TodoResponse, result)


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
