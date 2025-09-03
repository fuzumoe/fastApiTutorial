# 🚀 FastAPI Middleware — Beginner’s Guide

Middleware is like a **filter** that every request and response passes through.
It sits **between the client** and your **API endpoints**.

---

## 🔎 What is Middleware?

Think of it like an **airport security check**:

- ✈️ **Passenger (request)** arrives.
- 🛂 Security **checks bags, scans, maybe adds stamps**.
- 🎯 Passenger continues to **boarding gate (API endpoint)**.
- 🛬 On the way out, security may **add notes, log details** before leaving.

---

## 📊 Illustration

```
Client ---> [ Middleware ] ---> API Endpoint
   ^                                 |
   |                                 v
   <--- [ Middleware ] <--- Response
```

Middleware runs **before and after** the actual request handler.

---

## 🧩 Function-Based Middleware

This is the **simplest** way in FastAPI.

```python
from fastapi import FastAPI, Request, Response
from typing import Awaitable, Callable
import time

app = FastAPI()

CallNext = Callable[[Request], Awaitable[Response]]

@app.middleware("http")
async def log_requests(request: Request, call_next: CallNext) -> Response:
    start_time: float = time.time()

    response: Response = await call_next(request)

    process_time: float = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    print(f"[Middleware] {request.method} {request.url} took {process_time:.4f}s")

    return response

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, Middleware!"}
```

---

## 🧩 Class-Based Middleware

Sometimes you want more **control** or **reusability**.
Then you can use a class with `BaseHTTPMiddleware`.

```python
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start_time
        response.headers["X-Duration"] = f"{duration:.6f}"
        print(f"[ClassMiddleware] {request.method} {request.url} took {duration:.4f}s")
        return response

app = FastAPI()
app.add_middleware(LogRequestsMiddleware)

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello from class-based middleware"}
```

---

## 📦 Built-in Middleware

FastAPI (via Starlette) gives you ready-to-use middleware:

- `CORSMiddleware` → Handle cross-origin requests.
- `GZipMiddleware` → Compress responses.
- `TrustedHostMiddleware` → Validate host headers.

Example:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all (unsafe for prod!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ When to Use Which?

| Type              | Best for ✅                          |
|-------------------|--------------------------------------|
| Function-based    | Simple, project-specific logic       |
| Class-based       | Reusable, configurable middlewares   |
| Built-in          | Common needs (CORS, GZip, etc.)      |

---

## 🎯 Key Takeaways

- Middleware is code that runs **before and after** every request.
- Use it for **logging, timing, auth, headers, compression, etc.**
- Start with **function-based** middleware.
- Use **class-based** when you need flexibility or reuse.

---

## 📚 References

- [FastAPI Middleware Docs](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette Middleware Docs](https://www.starlette.io/middleware/)
- [FastAPI Advanced User Guide](https://fastapi.tiangolo.com/advanced/)
- [FastAPI GitHub Repository](https://github.com/tiangolo/fastapi)
