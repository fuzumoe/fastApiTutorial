"""
1. What is a Decorator?
A decorator is just a function that takes another function as input, adds extra behavior, and returns a new function.

It’s like wrapping a gift:

🎁 The gift = your original function.

🎀 The ribbon = extra behavior you add with the decorator.

2. Why use decorators?
To avoid repeating code.

To add functionality without changing the original function’s code.

To separate core logic from extra logic like logging, timing, authentication, etc.
"""

# 3. Basic example without decorator syntax
from collections.abc import Callable
from functools import wraps
from typing import Any


def greet() -> None:
    print("Hello, world!")  # noqa: T201


def my_decorator(func: Callable[[], None]) -> Callable[..., None]:
    def wrapper() -> None:
        print("Before the function runs")  # noqa: T201
        func()
        print("After the function runs")  # noqa: T201

    return wrapper


# Apply the decorator manually
decorated_greet = my_decorator(greet)
decorated_greet()


# 4. Using the @ decorator syntax (shortcut)
# instead of decorated_greet = my_decorator(greet)
@my_decorator
def greet_alt() -> None:
    print("Hello, world!")  # noqa: T201


greet_alt()


# 5. Decorators with arguments
def my_decorator_with_args(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print("Before function")  # noqa: T201
        result = func(*args, **kwargs)
        print("After function")  # noqa: T201
        return result

    return wrapper


@my_decorator_with_args
def add(a: int, b: int) -> int:
    print(f"Adding {a} + {b}")  # noqa: T201
    return a + b


print(add(5, 3))  # noqa: T201

# 6. Decorotoers with arguments

from collections.abc import Callable  # noqa: E402
from typing import Any, TypeVar  # noqa: E402

T = TypeVar("T")  # Declare type variable for return type


def repeat(
    times: int = 1,
) -> Callable[[Callable[..., T]], Callable[..., T]]:  # decorator arguments live here
    def decorator(func: Callable[..., T]) -> Callable[..., T]:  # the real decorator
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Call function at least once to ensure we have a valid return value of type T
            actual_times = max(1, times)
            result: T = func(*args, **kwargs)
            for _ in range(actual_times - 1):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator  # ③ return the decorator


@repeat(times=3)
def hello(name: str) -> None:
    print(f"hi {name}!")  # noqa: T201


hello("Ada")
# prints "hi Ada!" three times


def log(prefix: str = "[LOG]") -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            print(f"{prefix} calling {func.__name__}")  # noqa: T201
            return func(*args, **kwargs)

        return wrapper

    return decorator


@log(prefix=">>>")
def add_numbers(a: int, b: int) -> int:
    return a + b


print(add_numbers(2, 5))  # noqa: T201
# >>> calling add_numbers
# 7
