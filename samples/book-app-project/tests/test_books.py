import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
import book_app
from books import Book, BookCollection, get_book_statistics


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False


def test_search_matches_title_or_author_case_insensitively():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("Dune", "Frank Herbert", 1965)

    title_matches = collection.search("HOB")
    author_matches = collection.search("herbert")

    assert [book.title for book in title_matches] == ["The Hobbit"]
    assert [book.title for book in author_matches] == ["Dune"]


def test_search_returns_no_books_for_empty_query():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)

    assert collection.search("   ") == []


def test_search_command_displays_matching_books(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    monkeypatch.setattr(book_app, "collection", collection)
    monkeypatch.setattr("builtins.input", lambda _: "herb")

    book_app.handle_search()

    captured = capsys.readouterr()
    assert "Dune by Frank Herbert" in captured.out


def test_search_command_reports_no_results(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    monkeypatch.setattr(book_app, "collection", collection)
    monkeypatch.setattr("builtins.input", lambda _: "unknown")

    book_app.handle_search()

    captured = capsys.readouterr()
    assert "No books found." in captured.out


def test_filter_books_by_status_author_and_year():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("Children of Dune", "Frank Herbert", 1976)
    collection.add_book("1984", "George Orwell", 1949)
    collection.mark_as_read("Dune")

    books = collection.filter_books(
        status="read",
        author="HERBERT",
        year=1965,
    )

    assert [book.title for book in books] == ["Dune"]


def test_filter_books_returns_all_books_without_criteria():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("1984", "George Orwell", 1949)

    books = collection.filter_books(status="all")

    assert [book.title for book in books] == ["Dune", "1984"]


def test_mark_read_command_marks_book(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    monkeypatch.setattr(book_app, "collection", collection)
    monkeypatch.setattr("builtins.input", lambda _: "Dune")

    book_app.handle_mark_read()

    captured = capsys.readouterr()
    assert "Book marked as read." in captured.out
    assert collection.find_book_by_title("Dune").read is True


def test_mark_read_command_reports_missing_book(monkeypatch, capsys):
    collection = BookCollection()
    monkeypatch.setattr(book_app, "collection", collection)
    monkeypatch.setattr("builtins.input", lambda _: "Unknown")

    book_app.handle_mark_read()

    captured = capsys.readouterr()
    assert "Book not found." in captured.out


def test_search_command_reports_empty_query(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: " ")

    book_app.handle_search()

    captured = capsys.readouterr()
    assert "Search text cannot be empty." in captured.out


def test_filter_command_reports_invalid_status(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "finished")

    book_app.handle_filter()

    captured = capsys.readouterr()
    assert "Status must be all, read, or unread." in captured.out


def test_filter_command_reports_invalid_year(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "all" if "Status" in _ else "not-a-year")

    book_app.handle_filter()

    captured = capsys.readouterr()
    assert "Publication year must be a number." in captured.out


def test_filter_command_displays_matching_books(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("1984", "George Orwell", 1949)
    monkeypatch.setattr(book_app, "collection", collection)
    inputs = iter(["all", "Frank", "1965"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    book_app.handle_filter()

    captured = capsys.readouterr()
    assert "Dune by Frank Herbert" in captured.out
    assert "1984 by George Orwell" not in captured.out


def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_add_book_rejects_blank_title_and_author():
    collection = BookCollection()

    with pytest.raises(ValueError, match="title cannot be empty"):
        collection.add_book("   ", "George Orwell", 1949)

    with pytest.raises(ValueError, match="author cannot be empty"):
        collection.add_book("1984", "   ", 1949)


def test_book_rejects_negative_year():
    with pytest.raises(ValueError, match="Year must be zero or greater"):
        Book("1984", "George Orwell", -1)


def test_get_book_statistics():
    books_to_summarize = [
        Book("1984", "George Orwell", 1949, read=True),
        Book("Dune", "Frank Herbert", 1965),
        Book("The Hobbit", "J.R.R. Tolkien", 1937, read=True),
    ]

    statistics = get_book_statistics(books_to_summarize)

    assert statistics["total_count"] == 3
    assert statistics["read_count"] == 2
    assert statistics["unread_count"] == 1
    assert statistics["oldest"].title == "The Hobbit"
    assert statistics["newest"].title == "Dune"


def test_get_book_statistics_for_empty_list():
    statistics = get_book_statistics([])

    assert statistics == {
        "total_count": 0,
        "read_count": 0,
        "unread_count": 0,
        "oldest": None,
        "newest": None,
    }
