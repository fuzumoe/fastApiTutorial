from datetime import datetime
from typing import Any


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


def patch_todo(todo_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    todo = None
    for t in todos:
        if t["id"] == todo_id:
            todo = t
            break
    if todo:
        todo.update(updates)
        return todo
    return None


def update_todo(todo_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    todo = None
    for t in todos:
        if t["id"] == todo_id:
            todo = t
            break
    if todo:
        todo.update(updates)
        return todo
    return None


def delete_todo(todo_id: int) -> bool:
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return True
