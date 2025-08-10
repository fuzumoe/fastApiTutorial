# FastAPI Tutorial with Beanie ODM and Docker

This project demonstrates how to build a modern REST API using FastAPI with MongoDB database integration via Beanie ODM, all containerized with Docker.

## Beanie ODM Integration

[Beanie](https://beanie-odm.dev/) is an asynchronous Python ODM (Object-Document Mapper) for MongoDB, built on top of [Motor](https://motor.readthedocs.io/) and [Pydantic](https://pydantic-docs.helpmanual.io/). It allows you to define MongoDB document structures using Python classes with type hints.

### Document Model Definition

In our application, we define a `Todo` document model:

```python
class Todo(Document):
    task: str
    completed: bool
    time: datetime
    priority: int
    rate: float

    class Settings:
        name = "todos"  # MongoDB collection name
```

This class:
1. Inherits from Beanie's `Document` class
2. Defines fields with Python type annotations
3. Specifies the MongoDB collection name in the inner `Settings` class

### Database Initialization

The database connection is initialized in the `init()` function:

```python
async def init(app: FastAPI) -> None:
    # Create MongoDB client
    client: motor.motor_asyncio.AsyncIOMotorClient = (
        motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    )
    # Store client in app state for later access
    app.state.mongo_client = client

    # Get database
    db = client[MONGO_DB]

    # Initialize Beanie with database and document models
    await init_beanie(database=cast(Any, db), document_models=[Todo])
```

This function:
1. Creates an async MongoDB client using connection details from environment variables
2. Stores the client in the FastAPI app's state
3. Initializes Beanie with the database and document models

### Data Management Functions

We've implemented two key data management functions:

#### Remove All Data

```python
async def remove_all_data() -> None:
    logger.info("Removing all todos...")
    await Todo.delete_all()
    logger.info("All todos removed.")
```

This function deletes all documents from the `todos` collection using Beanie's `delete_all()` method.

#### Populate Initial Data

```python
async def populate_data() -> None:
    logger.info("No todos found, populating initial data...")
    initial_todos = []
    for todo_data in todos:
        todo_dict = dict(todo_data)
        todo_dict.pop("id", None)  # Remove ID field as MongoDB will generate it
        initial_todos.append(Todo(**todo_dict))

    await Todo.insert_many(initial_todos)
    logger.info("Initial data populated.")
```

This function:
1. Creates Todo objects from a predefined list of dictionaries
2. Removes the `id` field from each dictionary (since MongoDB will generate IDs)
3. Inserts all todos at once using Beanie's `insert_many()` method

## Application Lifecycle Management

FastAPI supports dependency injection and lifecycle event handlers. In our application, we use the `lifespan` context manager to handle startup and shutdown events:

```python
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
```

This context manager:

1. **On startup**:
   - Initializes the database connection
   - Removes existing data (for a clean start)
   - Populates initial data

2. **On shutdown**:
   - Closes the MongoDB client connection
   - Handles any exceptions gracefully

3. **Error handling**:
   - Logs errors that occur during startup or shutdown
   - Ensures the application can still start even if there's a database error

The `lifespan` parameter is passed to the FastAPI application constructor:

```python
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
```

## Docker Integration

Our project uses Docker to containerize both the FastAPI application and the MongoDB database, making it easy to develop and deploy consistently across different environments.

### Docker Compose Configuration

The `docker-compose.yml` file defines the services:

```yaml
services:
  mongodb:
    image: mongo:6.0
    container_name: mongodb
    ports:
      - "${MONGO_PORT}:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGO_DB}
    command: ["--auth", "--bind_ip_all"]   # enforce auth
    volumes:
      - mongodb_data:/data/db
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mongodb_data:
```

This configuration:

1. **MongoDB Service**:
   - Uses the official MongoDB 6.0 image
   - Maps the container's port 27017 to `${MONGO_PORT}` on the host
   - Sets environment variables for database initialization
   - Enables authentication with `--auth`
   - Persists data using a named volume (`mongodb_data`)
   - Includes a healthcheck to verify the database is running

2. **Environment Variables**:
   - Uses variable substitution (`${VARIABLE_NAME}`) to read from host environment or `.env` file
   - Makes the configuration flexible across different environments

### Running with Docker Compose

To start the services:

```bash
docker-compose up -d
```

To stop the services:

```bash
docker-compose down
```

To view logs:

```bash
docker-compose logs -f
```

### Environment Variables

The application reads environment variables with sensible defaults:

```python
# App
APP_NAME = os.getenv("APP_NAME", "FastAPI Tutorial")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple FastAPI application")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Database
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27019"))
MONGO_DB = os.getenv("MONGO_DB", "fastapi_tutorial")
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "example")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_AUTH_SOURCE}"
```

For local development, these defaults work with the Docker Compose configuration. In production, you should set these variables to appropriate values.

## API Documentation

The application provides multiple API documentation options:

1. **Swagger UI**: Available at `/docs` endpoint
2. **ReDoc**: Available at `/redoc` endpoint
3. **Scalar**: Available at `/scalar` endpoint (a more modern alternative)

Documentation is automatically generated from your route definitions and Pydantic models.

## References

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI GitHub Repository](https://github.com/tiangolo/fastapi)

### Beanie ODM
- [Beanie Documentation](https://beanie-odm.dev/)
- [Beanie GitHub Repository](https://github.com/roman-right/beanie)

### MongoDB
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Motor Documentation](https://motor.readthedocs.io/)

### Docker
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### VS Code
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Python in VS Code](https://code.visualstudio.com/docs/languages/python)
