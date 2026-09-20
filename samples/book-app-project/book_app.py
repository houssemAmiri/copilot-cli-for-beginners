import sys
from collections.abc import Callable

from books import Book, BookCollection


# Global collection instance
collection = BookCollection()


def show_books(books: list[Book]) -> None:
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()


def handle_list() -> None:
    books = collection.list_books()
    show_books(books)


def handle_add() -> None:
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        year = int(year_str) if year_str else 0
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValueError as e:
        print(f"\nError: {e}\n")


def handle_remove() -> None:
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    collection.remove_book(title)

    print("\nBook removed if it existed.\n")


def handle_mark_read() -> None:
    print("\nMark a Book as Read\n")

    title = input("Enter the title of the book to mark as read: ").strip()
    if collection.mark_as_read(title):
        print("\nBook marked as read.\n")
    else:
        print("\nBook not found.\n")


def handle_find() -> None:
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    books = collection.find_by_author(author)

    show_books(books)


def handle_search() -> None:
    print("\nSearch Books\n")

    query = input("Search title or author: ").strip()
    if not query:
        print("\nSearch text cannot be empty.\n")
        return

    show_books(collection.search(query))


def handle_filter() -> None:
    print("\nFilter Books\n")

    status = input("Status (all, read, unread): ").strip().lower()
    if status not in {"", "all", "read", "unread"}:
        print("\nStatus must be all, read, or unread.\n")
        return

    author = input("Author (optional): ").strip()
    year_input = input("Publication year (optional): ").strip()
    year = None
    if year_input:
        try:
            year = int(year_input)
        except ValueError:
            print("\nPublication year must be a number.\n")
            return

    books = collection.filter_books(
        status=status or "all",
        author=author or None,
        year=year,
    )
    show_books(books)


def show_help() -> None:
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  mark-read - Mark a book as read
  find     - Find books by author
  search   - Search titles and authors
  filter   - Filter by status, author, or year
  help     - Show this help message
""")


COMMAND_HANDLERS: dict[str, Callable[[], None]] = {
    "list": handle_list,
    "add": handle_add,
    "remove": handle_remove,
    "mark-read": handle_mark_read,
    "find": handle_find,
    "search": handle_search,
    "filter": handle_filter,
    "help": show_help,
}


def main() -> None:
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        print("Unknown command.\n")
        show_help()
        return

    handler()


if __name__ == "__main__":
    main()
