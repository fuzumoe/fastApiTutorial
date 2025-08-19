# Python 3.10+ ONLY (use built-in generics: list, dict, tuple, and | for unions)
from typing import TypeAlias

# Type alias definitions
StudentInfo: TypeAlias = dict[str, str | list[str]]
StudentRecord: TypeAlias = tuple[int, str, list[str]]
BookInfo: TypeAlias = dict[str, str | int]


def find_max(numbers: list[float | int]) -> float | int | None:
    """Return the maximum number in the list, or None if empty."""
    if not numbers:
        return None
    return max(numbers)


def word_frequencies(words: list[str]) -> dict[str, int]:
    """Return a dictionary mapping each word to its frequency."""
    freq: dict[str, int] = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq


def get_student_record(
    student_id: int, student_data: dict[int, StudentInfo]
) -> StudentRecord | None:
    """
    Return a tuple of (id, name, courses) for the given student_id.
    courses is a list of course names.
    Return None if not found.
    """
    data = student_data.get(student_id)
    if not data:
        return None
    return (student_id, data["name"], data["courses"])  # type: ignore


def average_grades(grades: list[float]) -> float | None:
    """Return the average of grades in the list, rounded to 2 decimals; None if empty."""
    if not grades:
        return None
    return round(sum(grades) / len(grades), 2)


class Library:
    def __init__(self) -> None:
        self.books: dict[str, BookInfo] = {}

    def add_book(self, title: str, author: str, year: int) -> None:
        self.books[title] = {"author": author, "year": year}

    def find_books_by_author(self, author: str) -> list[str]:
        return [title for title, info in self.books.items() if info["author"] == author]


# Example usage (should still run after you add hints)
numbers: list[float | int] = [10, 20, 30]
print(find_max(numbers))

words = ["apple", "banana", "apple", "cherry"]
print(word_frequencies(words))

students: dict[int, StudentInfo] = {
    1: {"name": "Alice", "courses": ["Math", "Physics"]},
    2: {"name": "Bob", "courses": ["History"]},
}
print(get_student_record(1, students))

grades = [85.5, 90.0, 78.5]
print(average_grades(grades))

lib = Library()
lib.add_book("1984", "George Orwell", 1949)
lib.add_book("Animal Farm", "George Orwell", 1945)
print(lib.find_books_by_author("George Orwell"))
