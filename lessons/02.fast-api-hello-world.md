# FastAPI Hello World Tutorial

This lesson introduces you to FastAPI by building a simple "Hello World" application. FastAPI is a modern, fast (high-performance) web framework for building APIs with Python based on standard Python type hints.

## Prerequisites

- Python 3.12+ installed
- Basic knowledge of Python
- Understanding of HTTP requests and APIs

## Installation

### Required Libraries for FastAPI Development

To build a complete FastAPI application, you'll need several packages:

| Package | Purpose |
|---------|---------|
| `fastapi` | The core web framework |
| `uvicorn` | ASGI server to run your application |
| `pydantic` | Data validation and settings management (included with FastAPI) |
| `python-multipart` | For form data parsing |
| `requests` | For making HTTP requests from your app |
| `PyJWT` | For JSON Web Token authentication |
| `fastapi-cli` | Command line tools for FastAPI development |
| `python-jose[cryptography]` | For more advanced JWT with cryptography support |

### Basic Installation

Using uv (recommended for speed and dependency management):

```bash
uv add fastapi uvicorn
```

For a complete development setup:

```bash
uv add fastapi uvicorn python-multipart requests PyJWT fastapi-cli python-jose[cryptography]
```

If you prefer traditional pip:

```bash
pip install fastapi uvicorn
```

## Understanding Our Hello World Application

Let's break down our `main.py` file:

```python
import os
from fastapi import FastAPI
import uvicorn

# Get environment variables with defaults
APP_NAME = os.getenv("APP_NAME", "FastAPI Tutorial")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple FastAPI application")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Create FastAPI instance
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Define a route
@app.get("/")
async def hello_world() -> dict[str, str]:
    return {"message": f"Hello from {APP_NAME}!"}

# Original main function (can be used for non-API functionality)
def main() -> None:
    print(f"Hello from {APP_NAME}!")
    return None

# Run the API with uvicorn when script is executed
if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
```

### Code Explanation

1. **Imports**:
   - `os`: Used to access environment variables
   - `FastAPI`: The main class from FastAPI
   - `uvicorn`: ASGI server for running our FastAPI application

2. **Environment Variables**:
   - We use `os.getenv()` to get configuration from environment variables
   - Default values are provided if environment variables aren't set
   - This makes our app configurable without changing code

3. **FastAPI Instance**:
   - We create an instance of `FastAPI` with metadata like title and version
   - This metadata is used in the automatic API documentation

4. **Route Definition**:
   - `@app.get("/")` is a decorator that tells FastAPI this function handles GET requests to "/"
   - Our function returns a JSON object with a greeting message
   - Type annotations (`-> dict[str, str]`) help FastAPI validate and document the response

5. **Main Function**:
   - A simple function to demonstrate non-API usage
   - Returns `None` as specified by the type annotation

6. **Running the Application**:
   - When script is run directly, we start the Uvicorn server
   - We pass configuration from our environment variables

## Running the Application

There are multiple ways to run this FastAPI application. Let's explore each method with its advantages:

### Method 1: Using Python directly

```bash
python main.py
```

**How it works:**
- This runs your Python script directly, which in turn calls `uvicorn.run()` from your code
- Uses the environment variables and defaults defined in your script
- Simple and straightforward - just one command to remember

**Best when:**
- You want to use the configuration defined in your code
- You're explaining the application to beginners
- You want to maintain the same startup configuration across environments

### Method 2: Using Uvicorn CLI directly

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**How it works:**
- Directly calls the Uvicorn ASGI server to run your application
- `main:app` refers to the `app` object in the `main.py` file
- Parameters override any defaults in your code

**Best when:**
- You need to override settings without changing code
- You're working with different environments
- You need more control over server parameters

### Method 3: Using FastAPI CLI tools

FastAPI provides several CLI tools to enhance your development experience. First, install the FastAPI CLI package:

```bash
uv add fastapi-cli
```

#### Using fastapi run

The most basic command is `fastapi run` which is a wrapper around uvicorn with sensible defaults:

```bash
fastapi run main:app --reload
```

**How it works:**
- Similar to uvicorn but with pre-configured settings
- Handles common configuration automatically
- Still requires you to specify the application module

#### Using fastapi dev

For an enhanced development experience with hot-reloading and debugging tools:

```bash
fastapi dev
```

or with specific module:

```bash
fastapi dev main:app
```

**How it works:**
- Simply running `fastapi dev` in your project directory will automatically detect your FastAPI app
- Starts a development server with best-practice settings
- Provides enhanced error messages and colorful logs
- Includes automatic reloading on code changes
- Offers improved debugging information

**Best when:**
- You're actively developing and debugging
- You want the simplest possible command to run your app
- You need the most developer-friendly experience

#### Comparison of Methods

| Method | Command | Ease of Use | Customization | Dev Features |
|--------|---------|-------------|--------------|--------------|
| Python | `python main.py` | ★★★★☆ | ★★☆☆☆ | ★☆☆☆☆ |
| Uvicorn | `uvicorn main:app` | ★★★☆☆ | ★★★★★ | ★★☆☆☆ |
| FastAPI Run | `fastapi run main:app` | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |
| FastAPI Dev | `fastapi dev` | ★★★★★ | ★★☆☆☆ | ★★★★★ |

#### Additional CLI features

FastAPI CLI also offers:

```bash
# Create a new project scaffold
fastapi new my-project

# Run tests
fastapi test

# Generate OpenAPI schema
fastapi schema main:app -o openapi.json
```

These tools streamline the development workflow, especially for beginners.

## Exploring Your API

Once running, you can:

1. **Access your API**: Visit http://127.0.0.1:8000 in your browser or use tools like curl:
   ```bash
   curl http://127.0.0.1:8000
   ```
   You should see: `{"message":"Hello from FastAPI Tutorial!"}`

2. **Interactive API documentation**: FastAPI automatically generates interactive documentation:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

3. **OpenAPI Schema**: Access your API's OpenAPI schema at http://127.0.0.1:8000/openapi.json

## Using Environment Variables

Our app reads configuration from environment variables. You can set these before running:

```bash
# Unix/Linux/Mac
export APP_NAME="My Custom API"
export PORT=9000

# Windows
set APP_NAME=My Custom API
set PORT=9000
```

Or create a `.env` file in your project root with:

```
APP_NAME=My Custom API
PORT=9000
```

## Package Management with uv

In this tutorial, we're using `uv` as our Python package manager. It's a faster alternative to pip with improved dependency resolution.

### Basic uv Commands

```bash
# Install packages
uv add package-name

# Install multiple packages
uv add package1 package2 package3

# Install specific versions
uv add fastapi==0.100.0

# Install from requirements.txt
uv pip sync requirements.txt

# Create/update lockfile
uv pip compile requirements.txt -o uv.lock

# Create a new virtual environment
uv venv

# Install development dependencies
uv add --dev pytest pytest-cov black
```

### Setting Up a FastAPI Project with uv

Here's a complete setup process for a new FastAPI project:

```bash
# Create project directory
mkdir my_fastapi_project && cd my_fastapi_project

# Create virtual environment
uv venv

# Activate environment (Unix/macOS)
source .venv/bin/activate

# Activate environment (Windows)
.venv\Scripts\activate

# Install core dependencies
uv add fastapi uvicorn

# Install development dependencies
uv add --dev pytest httpx

# Create lockfile
uv pip freeze > requirements.txt
uv pip compile requirements.txt -o uv.lock
```

The `uv.lock` file ensures reproducible builds across different environments.

**Why uv?**
- Up to 10-100x faster than pip
- Better dependency resolution
- Lockfile support for reproducible environments
- Compatible with pip's command structure
- Built-in virtual environment management

## Next Steps

Try these modifications to learn more:
1. Add a new route with a different path
2. Return different types of data
3. Add path parameters to your routes
4. Add query parameters
5. Explore request bodies and POST methods

FastAPI's official documentation is excellent for further learning: https://fastapi.tiangolo.com/
