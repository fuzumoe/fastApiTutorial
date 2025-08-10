# FastAPI Dependencies and Type Annotations

This lesson covers dependency injection in FastAPI and advanced Python type annotations, both of which are essential for building maintainable, testable, and type-safe APIs.

## FastAPI Dependency Injection

Dependency injection is a design pattern where objects receive their dependencies instead of creating them. In FastAPI, this pattern is implemented using the `Depends` function, which allows you to:

1. Reuse shared logic across multiple endpoints
2. Apply middleware-like functionality to specific routes
3. Organize your code into modular, testable components
4. Automatically validate and parse parameters

### Basic Dependencies

The simplest form of dependency is a function that returns a value:

```python
async def get_greeting() -> str:
    return "Hello from a dependency!"

@app.get("/greet")
async def greet_with_dependency(
    greeting: Annotated[str, Depends(get_greeting)],
) -> dict[str, str]:
    return {"msg": greeting}
```

When a request is made to `/greet`, FastAPI:
1. Calls `get_greeting()`
2. Injects the return value into the `greeting` parameter
3. Executes the route function with this value

### Class-based Dependencies

For more complex dependencies, you can use classes:

```python
class GreeterService:
    def __init__(self, prefix: str = "Hello") -> None:
        self.prefix: str = prefix

    def greet(self, name: str) -> str:
        return f"{self.prefix}, {name}!"

def get_greeter() -> GreeterService:
    return GreeterService(prefix="Hello")

Greeter = Annotated[GreeterService, Depends(get_greeter)]

@app.get("/greet/{name}")
def greet(name: str, greeter: Greeter) -> dict[str, str]:
    return {"message": greeter.greet(name)}
```

This approach is useful when:
1. The dependency has multiple methods or properties
2. You need to maintain state between method calls
3. You want to mock or replace the dependency in tests

### Route-level Dependencies

You can apply dependencies to entire routes without injecting them:

```python
def require_api_key(request: Request) -> None:
    if request.headers.get("x-api-key") != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

@app.get("/protected", dependencies=[Depends(require_api_key)])
def protected() -> dict[str, bool]:
    return {"ok": True}
```

This pattern is ideal for:
1. Authentication and authorization checks
2. Rate limiting
3. Logging and monitoring
4. Access control

### Dependency Chaining

Dependencies can depend on other dependencies, creating chains:

```python
async def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

async def get_user_repo(db: Annotated[Database, Depends(get_db)]):
    return UserRepository(db)

@app.get("/users")
async def list_users(repo: Annotated[UserRepository, Depends(get_user_repo)]):
    return await repo.list()
```

### Benefits of Dependency Injection

1. **Testability**: Dependencies can be easily mocked in unit tests
2. **Reusability**: Common logic can be shared across endpoints
3. **Separation of concerns**: Each component has a specific responsibility
4. **Maintainability**: Code is more modular and easier to update

## Python Type Annotations

Type annotations add static type information to Python code, enhancing:
1. Code readability
2. IDE autocompletion and error checking
3. Static analysis through tools like mypy

### Basic Type Annotations

Python's typing system allows you to annotate variables and function signatures:

```python
# Variable type hints
text: str = "value"
pert: int = 90
temp: float = 37.5

# Function annotations
def add(a: int, b: int) -> int:
    return a + b
```

### Union Types

To indicate that a variable can be multiple types, use the union operator `|`:

```python
# Two possible types
number: int | float = 12
```

### Collection Types

Generic types let you specify container element types:

```python
# Sequence datatype
digits: list[int] = [1, 2, 3, 4, 5]

# Fixed tuple with specific types
pair: tuple[str, int] = ("answer", 42)

# Variable length tuple with same type
table_5: tuple[int, ...] = (5, 10, 15, 20, 25)

# Dictionary key and value hinting
shipment: dict[str, Any] = {
    "id": 12701,
    "weight": 1.2,
    "content": "wooden table",
    "status": "in transit",
}
```

### Custom Types

You can use your own classes as types:

```python
class City:
    def __init__(self, name: str, location: int):
        self.name = name
        self.location = location

hampshire = City("hampshire", 2048593)
city_temp: tuple[City, float] = (hampshire, 20.5)
```

### Callable Types

For functions and other callables:

```python
from collections.abc import Callable

def my_callback(user_id: int) -> None:
    pass

def another_callback(user_id: int) -> dict[str, Any]:
    return {"user_id": user_id}

x: Callable[[int], None] = my_callback
y: Callable[[int], dict[str, Any]] = another_callback

def process_data(
    data: dict[str, Any], callback: Callable[..., None]
) -> Callable[..., None]:
    user_id = data.get("user_id", 0)

    def proc_func(user_id: int) -> None:
        callback(user_id)

    return proc_func
```

### Annotated Type

The `Annotated` type lets you attach metadata to a type annotation without affecting runtime behavior:

```python
from typing import Annotated

UserID = Annotated[int, "User ID"]

def get_user(user_id: UserID) -> dict:
    return {"id": user_id}
```

In FastAPI, `Annotated` is used with `Depends` to specify dependencies:

```python
from fastapi import Depends, FastAPI
from typing import Annotated

app = FastAPI()

def get_api_key(api_key: str = Header(...)):
    return api_key

@app.get("/items/")
async def read_items(api_key: Annotated[str, Depends(get_api_key)]):
    return {"api_key": api_key}
```

## Combining Dependencies and Type Annotations in FastAPI

FastAPI leverages both type annotations and dependency injection to create a robust API framework:

1. **Parameter validation**: Type annotations define the shape of request data
2. **Dependency injection**: `Depends` injects required components
3. **Documentation**: Types generate OpenAPI schema docs
4. **Security**: Type-checked dependencies for authentication

### Best Practices

1. **Be explicit with types**: Use specific types rather than `Any` when possible
2. **Use dependency injection for cross-cutting concerns**: Auth, logging, database access
3. **Create reusable dependencies**: Abstract common patterns into shared dependencies
4. **Leverage type aliases with Annotated**: Define common dependency types
5. **Document your dependencies**: Add docstrings explaining what each dependency does

### Testing Dependencies

Mock dependencies in tests to isolate components:

```python
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def mock_greeter():
    return MagicMock(spec=GreeterService)

@pytest.fixture
def client(mock_greeter):
    app.dependency_overrides[get_greeter] = lambda: mock_greeter
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_greet_endpoint(client, mock_greeter):
    mock_greeter.greet.return_value = "Mocked greeting, World!"
    response = client.get("/greet/World")
    assert response.status_code == 200
    assert response.json() == {"message": "Mocked greeting, World!"}
```

## References

### FastAPI Documentation
- [Dependencies in FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)
- [Dependency Classes](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)

### Python Type Annotations
- [Python Type Hints PEP 484](https://peps.python.org/pep-0484/)
- [Annotated Type PEP 593](https://peps.python.org/pep-0593/)
- [mypy Documentation](https://mypy.readthedocs.io/)
