import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

# Get environment variables with defaults
APP_NAME = os.getenv("APP_NAME", "FastAPI Tutorial")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple FastAPI application")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Create FastAPI instance
app = FastAPI(title=APP_NAME, description=APP_DESCRIPTION, version=APP_VERSION)


# Define a route
@app.get("/")
async def hello_world() -> dict[str, str]:
    return {"message": f"Hello from {APP_NAME}!"}


# Original main function (can be used for non-API functionality)
def main() -> None:
    print(f"Hello from {APP_NAME}!")
    return


@app.get("/scalar")
async def get_scalar() -> HTMLResponse:
    content: HTMLResponse = get_scalar_api_reference(
        openapi_url=app.openapi_url, title=APP_NAME
    )
    return content


# Run the API with uvicorn when script is executed
if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
