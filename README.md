# FastAPI and Pydantic Tutorial

This project demonstrates how to build a RESTful API using FastAPI with Pydantic for data validation and serialization.

## FastAPI and Pydantic Lesson

### Introduction to Pydantic

Pydantic is a data validation and settings management library that uses Python type annotations to validate data structures. In FastAPI applications, Pydantic models serve several important purposes:

1. **Request Validation**: They define the shape of incoming requests, automatically validating data.
2. **Response Serialization**: They define the structure of API responses.
3. **Documentation**: They're used to auto-generate API documentation.

### Core Concepts Used in Our Project

#### 1. Basic Pydantic Models

We use `BaseModel` from Pydantic to define our data structures:

```python
class CreateTodoRequest(BaseModel):
    task: str
    completed: bool
    time: str
    priority: int
    rate: float
```

This model:
- Automatically validates incoming data against the specified types
- Rejects requests with missing fields or incorrect types
- Provides clear error messages if validation fails

#### 2. Optional Fields with Union Types

For partial updates (PATCH requests), we use union types with `None` to make fields optional:

```python
class PatchTodoRequest(BaseModel):
    task: str | None
    completed: bool | None
    time: str | None
    priority: int | None
    rate: float | None
```

This allows API clients to provide only the fields they want to update.

#### 3. Model Methods

Our code uses several important Pydantic model methods:

- **model_dump()**: Converts a Pydantic model to a dictionary
  ```python
  todo_dict = todo.model_dump()
  ```

- **model_validate()**: Creates a Pydantic model from a dictionary
  ```python
  return TodoResponse.model_validate(todo_dict)
  ```

- **model_dump(exclude_unset=True)**: Creates a dictionary with only the fields that were explicitly set
  ```python
  updates.model_dump(exclude_unset=True)
  ```

#### 4. Type Annotations for Responses

FastAPI uses the return type annotations to generate response schemas:

```python
@app.post("/todos")
async def create_todo(todo: CreateTodoRequest | list[CreateTodoRequest]) -> TodoResponse | list[TodoResponse]:
```

#### 5. Complex Input Handling

Our API can handle both single items and lists of items in the same endpoint:

```python
@app.post("/todos")
async def create_todo(todo: CreateTodoRequest | list[CreateTodoRequest]) -> TodoResponse | list[TodoResponse]:
    if isinstance(todo, list):
        # Handle list of todos
    else:
        # Handle single todo
```

### Best Practices Demonstrated

1. **Separation of Concerns**: Different models for different operations (create, update, response)
2. **Consistent API Design**: Using HTTP methods correctly (GET, POST, PUT, PATCH, DELETE)
3. **Type Safety**: Using Python type annotations throughout
4. **Validation at the Edge**: Validating all incoming data before processing

### Pydantic Advanced Features (not used but worth mentioning)

1. **Field Validators**: Custom validation logic for fields
2. **Config Classes**: Customizing model behavior
3. **Schema Customization**: Adjusting the JSON Schema generation

## References

### Pydantic Documentation

- [Pydantic Official Documentation](https://docs.pydantic.dev/)
- [Models](https://docs.pydantic.dev/latest/usage/models/)
- [Field Types](https://docs.pydantic.dev/latest/api/types/)
- [Validation](https://docs.pydantic.dev/latest/usage/validators/)
- [Schema](https://docs.pydantic.dev/latest/usage/schema/)

### FastAPI Documentation

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Data Validation with Pydantic](https://fastapi.tiangolo.com/tutorial/body/)
- [Response Models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Request Body](https://fastapi.tiangolo.com/tutorial/body-multiple-params/)

### Additional Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [JSON Schema](https://json-schema.org/)
