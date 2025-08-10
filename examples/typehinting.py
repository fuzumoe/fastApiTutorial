from collections.abc import Callable
from typing import Annotated, Any


# Custom class as type
class City:
    def __init__(self, name: str, location: int):
        self.name = name
        self.location = location


# Variable type hints
text: str = "value"
pert: int = 90
temp: float = 37.5

# Two possible types
number: int | float = 12

# Sequence datatype
digits: list[int] = [1, 2, 3, 4, 5]

# Tuple like a list
table_5: tuple[int, ...] = (5, 10, 15, 20, 25)

# Tuple with 2 elements
hampshire = City("hamspshire", 2048593)
city_temp: tuple[City, float] = (hampshire, 20.5)

# Dictionary key and value hinting
shipment: dict[str, Any] = {
    "id": 12701,
    "weight": 1.2,
    "content": "wooden table",
    "status": "in transit",
}


def process_data(
    data: dict[str, Any], callback: Callable[..., None]
) -> Callable[..., None]:
    user_id: UserID = data.get("user_id", 0)  # Provide default value to avoid None

    def proc_func(user_id: UserID) -> None:
        callback(user_id)

    proc_func(user_id)
    return proc_func  # Add the missing return statement


# example of Callable typehints


def my_callback(user_id: int) -> None:
    pass


def another_callback(user_id: int) -> dict[str, Any]:
    return {"user_id": user_id}


x: Callable[[int], None] = my_callback
y: Callable[[int], dict[str, Any]] = another_callback

# EXAMPLE FOR Annotated

UserID = Annotated[int, "User ID"]
