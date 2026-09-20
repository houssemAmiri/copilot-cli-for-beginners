from books import Book


def print_menu():
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def get_user_choice() -> str:
    while True:
        choice = input("Choose an option (1-5): ").strip()

        if not choice:
            print("Please enter a number from 1 to 5.")
            continue

        if not choice.isdigit():
            print("Please enter a valid number from 1 to 5.")
            continue

        if choice not in {"1", "2", "3", "4", "5"}:
            print("Please choose a number between 1 and 5.")
            continue

        return choice


def get_book_details() -> tuple[str, str, int]:
    """Prompt the user for a book's title, author, and publication year.

    This function repeatedly asks for the title and author until both are
    non-empty strings. It then reads the publication year, tries to convert it
    to an integer, and defaults to 0 if the entered value is not numeric.

    Returns:
        tuple[str, str, int]: A tuple containing the validated title, the
        validated author, and the publication year as an integer.

    Example:
        ("Dune", "Frank Herbert", 1965)
    """
    while True:
        title = input("Enter book title: ").strip()
        if title:
            break
        print("Title cannot be empty. Please try again.")

    while True:
        author = input("Enter author: ").strip()
        if author:
            break
        print("Author cannot be empty. Please try again.")

    year_input = input("Enter publication year: ").strip()
    try:
        year = int(year_input)
    except ValueError:
        print("Invalid year. Defaulting to 0.")
        year = 0

    return title, author, year


def print_books(books: list[Book]) -> None:
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()
