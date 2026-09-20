import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, TypedDict

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False

    def __post_init__(self) -> None:
        self.title = self._validate_text("title", self.title)
        self.author = self._validate_text("author", self.author)

        if not isinstance(self.year, int):
            raise TypeError("Year must be an integer.")
        if self.year < 0:
            raise ValueError("Year must be zero or greater.")

    @staticmethod
    def _validate_text(field_name: str, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty.")

        return cleaned_value


class BookStatistics(TypedDict):
    total_count: int
    read_count: int
    unread_count: int
    oldest: Optional[Book]
    newest: Optional[Book]


def get_book_statistics(books: List[Book]) -> BookStatistics:
    """Return summary statistics for a list of books."""
    if not books:
        return {
            "total_count": 0,
            "read_count": 0,
            "unread_count": 0,
            "oldest": None,
            "newest": None,
        }

    read_count = sum(book.read for book in books)
    return {
        "total_count": len(books),
        "read_count": read_count,
        "unread_count": len(books) - read_count,
        "oldest": min(books, key=lambda book: book.year),
        "newest": max(books, key=lambda book: book.year),
    }


class BookCollection:
    def __init__(self, data_file: Optional[str | Path] = None):
        self.data_file = Path(data_file) if data_file is not None else Path(DATA_FILE)
        self.books: List[Book] = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON file if it exists."""
        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            self.books = []
            return
        except json.JSONDecodeError:
            print(
                f"Warning: {self.data_file.name} is corrupted. Starting with empty collection."
            )
            self.books = []
            return
        except OSError as exc:
            raise OSError(f"Unable to read books from {self.data_file}: {exc}") from exc

        if not isinstance(data, list):
            print(
                f"Warning: {self.data_file.name} does not contain a valid book list. "
                "Starting with empty collection."
            )
            self.books = []
            return

        try:
            self.books = [Book(**book_data) for book_data in data]
        except (TypeError, ValueError):
            print(
                f"Warning: {self.data_file.name} contains invalid book data. "
                "Starting with empty collection."
            )
            self.books = []

    def save_books(self) -> None:
        """Save the current book collection to JSON."""
        try:
            with self.data_file.open("w", encoding="utf-8") as file:
                json.dump([asdict(book) for book in self.books], file, indent=2)
        except OSError as exc:
            raise OSError(f"Unable to save books to {self.data_file}: {exc}") from exc

    def add_book(self, title: str, author: str, year: int) -> Book:
        """Add a validated book and persist it to disk."""
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return list(self.books)

    def list_by_year(self, start: int, end: int) -> List[Book]:
        """Return books published between two years, inclusive."""
        if not isinstance(start, int) or not isinstance(end, int):
            raise TypeError("Start and end years must be integers.")
        if start > end:
            raise ValueError("Start year must be less than or equal to end year.")

        return [book for book in self.books if start <= book.year <= end]

    def find_book_by_title(self, title: str) -> Optional[Book]:
        normalized_title = self._normalize_text(title)
        for book in self.books:
            if book.title.lower() == normalized_title:
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        book = self.find_book_by_title(title)
        if book is None:
            return False

        book.read = True
        self.save_books()
        return True

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book is None:
            return False

        self.books.remove(book)
        self.save_books()
        return True

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        normalized_author = self._normalize_text(author)
        return [book for book in self.books if book.author.lower() == normalized_author]

    def search(self, query: str) -> List[Book]:
        """Find books whose title or author contains the query."""
        normalized_query = self._normalize_text(query)
        if not normalized_query:
            return []

        return [
            book
            for book in self.books
            if normalized_query in book.title.lower()
            or normalized_query in book.author.lower()
        ]

    def filter_books(
        self,
        status: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
    ) -> List[Book]:
        """Filter books by status, author text, and publication year."""
        if status is not None and not isinstance(status, str):
            raise TypeError("Status must be a string or None.")
        if author is not None and not isinstance(author, str):
            raise TypeError("Author must be a string or None.")
        if year is not None and not isinstance(year, int):
            raise TypeError("Publication year must be an integer or None.")

        normalized_status = status.strip().lower() if status else None
        normalized_author = author.strip().lower() if author else None
        if normalized_status not in {None, "all", "read", "unread"}:
            raise ValueError("Status must be all, read, or unread.")

        return [
            book
            for book in self.books
            if (
                normalized_status is None
                or normalized_status == "all"
                or (normalized_status == "read" and book.read)
                or (normalized_status == "unread" and not book.read)
            )
            and (normalized_author is None or normalized_author in book.author.lower())
            and (year is None or book.year == year)
        ]

    @staticmethod
    def _normalize_text(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("Value must be a string.")
        return value.strip().lower()
