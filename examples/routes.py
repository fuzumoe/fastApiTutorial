from typing import Any, Callable


routes: dict[str, Callable[..., Any]] = {}


def route(path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a route."""

    def register_route(func: Callable[..., Any]) -> Callable[..., Any]:
        routes[path] = func
        return func

    return register_route


@route("/hello")
def hello_world() -> dict[str, str]:
    return {"message": "Hello World!"}


@route("/goodbye")
def goodbye_world() -> dict[str, str]:
    return {"message": "Goodbye World!"}


request: str = ""

while request != "quit":
    request = input("Enter route path (or 'quit' to exit): ")
    if request in routes:
        func = routes[request]
        response = func()
        print(f"Response from {request}: {response}")
    elif request != "quit":
        print(f"No route found for: {request}")
