# Python 3.10+ ONLY (use built-in generics: list, dict, tuple, and | for unions)

def find_max(numbers):
    """Return the maximum number in the list, or None if empty."""
    if not numbers:
        return None
    return max(numbers)

def word_frequencies(words):
    """Return a dictionary mapping each word to its frequency."""
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq

def get_student_record(student_id, student_data):
    """
    Return a tuple of (id, name, courses) for the given student_id.
    courses is a list of course names.
    Return None if not found.
    """
    data = student_data.get(student_id)
    if not data:
        return None
    return (student_id, data["name"], data["courses"])

def average_grades(grades):
    """Return the average of grades in the list, rounded to 2 decimals; None if empty."""
    if not grades:
        return None
    return round(sum(grades) / len(grades), 2)

class Library:
    def __init__(self):
        self.books = {}

    def add_book(self, title, author, year):
        self.books[title] = {"author": author, "year": year}

    def find_books_by_author(self, author):
        return [title for title, info in self.books.items() if info["author"] == author]

# Example usage (should still run after you add hints)
numbers = [10, 20, 30]
print(find_max(numbers))

words = ["apple", "banana", "apple", "cherry"]
print(word_frequencies(words))

students = {
    1: {"name": "Alice", "courses": ["Math", "Physics"]},
    2: {"name": "Bob", "courses": ["History"]}
}
print(get_student_record(1, students))

grades = [85.5, 90.0, 78.5]
print(average_grades(grades))

lib = Library()
lib.add_book("1984", "George Orwell", 1949)
lib.add_book("Animal Farm", "George Orwell", 1945)
print(lib.find_books_by_author("George Orwell"))
