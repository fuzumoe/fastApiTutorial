"""
1. What are Generics in Python?

In Python, generics are a way to write type-safe and reusable code without tying yourself to a specific type.
They let you say: “This function/class works with some type, but I’ll decide later what that type is.”

2. When to Use Generics?

- When your code works the same way for multiple types.
= When you want type hints to be more specific than just Any.
"""

from typing import Any, Generic, TypeVar


# Example without generics:
def first_item_without_generics(items: list) -> Any:
    return items[0]


# with generics
T = TypeVar("T")  # placeholder for any type

U = TypeVar("U")  # another generic type


def first_item(items: list[T]) -> T:
    return items[0]


# 3. Basic Syntax
class PairWithoutGenerics:
    def __init__(self, first: Any, second: Any):
        self.first = first
        self.second = second


class PairWithGenerics(Generic[T, U]):
    def __init__(self, first: T, second: U):
        self.first = first
        self.second = second


pair_without_generics = PairWithGenerics("hello", 123)  # any, any
pair_without_generics = PairWithGenerics("hello", 123)  # T=str, U=int


# 5. Common Generic Containerss
# list and dict are the containers for other types
def lookup(dictionary: dict[str, int], key: str) -> int:
    return dictionary[key]
