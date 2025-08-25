# FastAPI Background Tasks — Detailed Lesson

Background tasks in FastAPI let you run code **after sending a response**. They are best for short, non-critical follow-ups like sending emails, writing logs, or pinging a webhook. Under the hood, they use Starlette’s `BackgroundTasks`.

---

## 1. What are Background Tasks?

- Run **after** the HTTP response is sent to the client.
- Executed **in-process** (inside the same worker process).
- Great for *short-lived*, *non-critical* jobs.
- Not suitable for long-running or durable tasks (use Celery, RQ, or Dramatiq for that).

---

## 2. Core Usage

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

async def send_email(to: str, subject: str, body: str):
    # Example async function that sends an email
    print(f"Sending email to {to} with subject '{subject}'")

@app.post("/signup")
async def signup(user: dict, background_tasks: BackgroundTasks):
    # Save the user to database here...

    # Add task to run after response is sent
    background_tasks.add_task(
        send_email,
        to=user["email"],
        subject="Welcome!",
        body="Thanks for joining!"
    )
    return {"status": "ok"}
```

---

## 3. How It Works

- You add tasks with:
  ```python
  background_tasks.add_task(func, *args, **kwargs)
  ```
- Multiple tasks are stored in a list and run **sequentially** after the response.
- If you need concurrency between tasks, use `asyncio.gather` inside one background task.

---

## 4. Best Practices

### ✅ Save first, then queue
```python
todo = Todo(**payload)
await todo.save()  # Save to DB
background_tasks.add_task(log_activity, str(todo.id), "create")
```

### ✅ Pass IDs, not objects
Avoid passing entire DB models; pass IDs and reload inside the task.

```python
async def log_activity(todo_id: str, action: str):
    todo = await Todo.get(todo_id)
    if todo:
        await Activities(todo=todo, action_type=action).insert()
```

### ✅ Keep tasks short
Tasks should be:
- Quick (milliseconds–seconds)
- Idempotent (safe to retry manually if needed)
- Non-critical (system works even if skipped)

---

## 5. Advanced Patterns

### a) Run several async tasks concurrently
```python
import asyncio

async def run_all(*coros):
    await asyncio.gather(*coros)

background_tasks.add_task(
    run_all,
    send_email(...),
    call_webhook(...),
    warm_cache(...)
)
```

### b) Cleanup after responses
Background tasks are also useful for cleaning temp files after a response finishes.

```python
from fastapi.responses import FileResponse

async def delete_temp_file(path: str):
    import os
    os.remove(path)

@app.get("/report")
async def get_report(background_tasks: BackgroundTasks):
    file_path = "temp/report.pdf"
    return FileResponse(file_path, background=background_tasks.add_task(delete_temp_file, file_path))
```

---

## 6. When *Not* to Use BackgroundTasks

Use a **task queue** (Celery, RQ, Dramatiq, Arq) instead of `BackgroundTasks` if you need:

- **Durability** (jobs survive crashes, retries, scheduling)
- **Heavy CPU tasks** (e.g., image/video processing)
- **Long-running jobs** (minutes+)

Background tasks are meant for lightweight “fire-and-forget” work.

---

## 7. Testing Background Tasks

- **Unit test the function** directly:
  ```python
  import pytest

  @pytest.mark.asyncio
  async def test_send_email():
      await send_email("test@example.com", "Hello", "Body")
  ```
- **Integration test with TestClient**:
  Background tasks run before the test client context closes, so assertions can happen right after the request.

---

## 8. End-to-End Example

```python
from fastapi import FastAPI, BackgroundTasks
from beanie import PydanticObjectId
from datetime import datetime, UTC

app = FastAPI()

async def create_activity(todo_id: str, action: str, details: str | None = None):
    todo = await Todo.get(PydanticObjectId(todo_id))
    if todo:
        await Activities(
            todo=todo,
            action_type=ActionType(action),
            details=details,
            timestamp=datetime.now(tz=UTC),
        ).insert()

@app.post("/todos", status_code=201)
async def create_todo(req: CreateTodoRequest, background_tasks: BackgroundTasks):
    payload = req.model_dump(exclude_unset=True)
    payload["time"] = payload.get("time") or datetime.now(tz=UTC)

    todo = Todo(**payload)
    await todo.save()

    background_tasks.add_task(
        create_activity,
        str(todo.id),
        ActionType.CREATE.value,
        f"Todo created: {todo.task}"
    )

    return {
        "id": str(todo.id),
        "task": todo.task,
        "completed": todo.completed,
        "time": todo.time.isoformat(),
        "priority": todo.priority,
        "rate": todo.rate,
    }
```

---

## 9. Quick Checklist

- [x] Keep tasks **short and lightweight**
- [x] **Save to DB first**, then enqueue task
- [x] Pass **IDs**, reload inside task
- [x] Don’t use request-scoped objects inside tasks
- [x] For heavy/critical jobs → use **Celery/RQ/Dramatiq**
- [x] Scale by running **multiple workers** in production

---

## References

1. [FastAPI Docs: Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
2. [Starlette Docs: Background Tasks](https://www.starlette.io/background/)
3. [FastAPI Docs: Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
4. [TestDriven.io: Background Tasks & Celery](https://testdriven.io/blog/fastapi-background-tasks/)
5. [FastAPI Deployment Guide (workers)](https://fastapi.tiangolo.com/deployment/server-workers/)
