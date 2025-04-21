import streamlit as st
import json
from pathlib import Path

# Constants
LIBRARY_FILE = "library.json"  # File to store book data

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'library' not in st.session_state:
        st.session_state.library = load_library()  # Load existing data
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "menu"  # Default view
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""  # For search functionality
    if 'search_type' not in st.session_state:
        st.session_state.search_type = "title"  # Default search by title

def load_library():
    """Load the library from a JSON file. Returns an empty list if file doesn't exist."""
    if not Path(LIBRARY_FILE).exists():
        return []  # No file → empty library
    
    try:
        with open(LIBRARY_FILE, 'r') as f:
            return json.load(f)  # Load existing books
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return []  # Fallback to empty list on error

def save_library():
    """Save the current library to a JSON file."""
    try:
        with open(LIBRARY_FILE, 'w') as f:
            json.dump(st.session_state.library, f)  # Write to file
    except Exception as e:
        st.error(f"Error saving library: {e}")

def display_menu():
    """Display the main menu with navigation buttons."""
    st.title("📚 Personal Library Manager")
    
    # Buttons in columns for better layout
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Book"):
            st.session_state.current_view = "add_book"
    with col2:
        if st.button("🔍 Search Books"):
            st.session_state.current_view = "search_books"
    with col3:
        if st.button("📊 Statistics"):
            st.session_state.current_view = "statistics"
    
    col4, col5, _ = st.columns(3)
    with col4:
        if st.button("📖 View All Books"):
            st.session_state.current_view = "view_all"
    with col5:
        if st.button("🗑️ Remove Book"):
            st.session_state.current_view = "remove_book"
    
    st.markdown("---")
    st.write(f"Total books in your library: {len(st.session_state.library)}")

def add_book_view():
    """Form to add a new book with validation."""
    st.title("Add a New Book")
    
    with st.form("add_book_form"):
        title = st.text_input("Title*", max_chars=100).strip()  # Required
        author = st.text_input("Author*", max_chars=50).strip()  # Required
        year = st.number_input("Publication Year*", min_value=0, max_value=2023, step=1)
        genre = st.text_input("Genre", max_chars=30).strip() or "Unknown"  # Default if empty
        read_status = st.checkbox("I've read this book")
        
        submitted = st.form_submit_button("Add Book")
        if submitted:
            if not title or not author:  # Validate required fields
                st.error("Title and Author are required fields")
                return
            
            # Create new book entry
            new_book = {
                'title': title,
                'author': author,
                'year': year,
                'genre': genre,
                'read': read_status
            }
            
            st.session_state.library.append(new_book)
            save_library()  # Auto-save
            st.success(f"'{title}' has been added to your library!")
            st.session_state.current_view = "menu"  # Return to menu
            st.rerun()  # Refresh UI

    if st.button("Back to Menu"):
        st.session_state.current_view = "menu"
        st.rerun()

def remove_book_view():
    """Interface to search and remove books."""
    st.title("Remove a Book")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        if st.button("Back to Menu"):
            st.session_state.current_view = "menu"
            st.rerun()
        return
    
    search_term = st.text_input("Search for books to remove").lower()
    
    # Filter books by search term (title or author)
    found_books = [
        b for b in st.session_state.library 
        if search_term in b['title'].lower() or 
        search_term in b['author'].lower()
    ] if search_term else st.session_state.library
    
    if not found_books:
        st.warning("No books found matching your search")
    else:
        for i, book in enumerate(found_books):
            col1, col2 = st.columns([4, 1])
            with col1:
                read_status = "✓" if book['read'] else "✗"
                st.write(f"**{book['title']}** by {book['author']} ({book['year']})")
                st.caption(f"Genre: {book['genre']} | Read: {read_status}")
            with col2:
                if st.button(f"Remove #{i+1}"):
                    st.session_state.library.remove(book)
                    save_library()  # Auto-save
                    st.success(f"Removed '{book['title']}'")
                    st.rerun()  # Refresh UI
    
    if st.button("Back to Menu"):
        st.session_state.current_view = "menu"
        st.rerun()

def search_books_view():
    """Search books by title or author."""
    st.title("Search Books")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        if st.button("Back to Menu"):
            st.session_state.current_view = "menu"
            st.rerun()
        return
    
    search_type = st.radio("Search by:", ["Title", "Author"])
    search_term = st.text_input(f"Enter {search_type.lower()} to search for").strip().lower()
    
    if search_term:
        if search_type == "Title":
            results = [b for b in st.session_state.library if search_term in b['title'].lower()]
        else:
            results = [b for b in st.session_state.library if search_term in b['author'].lower()]
        
        if not results:
            st.warning("No books found matching your search")
        else:
            st.success(f"Found {len(results)} book(s):")
            display_book_list(results)
    
    if st.button("Back to Menu"):
        st.session_state.current_view = "menu"
        st.rerun()

def view_all_books():
    """Display all books with sorting options."""
    st.title(f"Your Library ({len(st.session_state.library)} books)")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        if st.button("Back to Menu"):
            st.session_state.current_view = "menu"
            st.rerun()
        return
    
    # Sorting options
    sort_option = st.selectbox(
        "Sort by:", 
        ["Title (A-Z)", "Title (Z-A)", "Author (A-Z)", "Author (Z-A)", "Year (Newest)", "Year (Oldest)"]
    )
    
    # Apply sorting
    if sort_option == "Title (A-Z)":
        sorted_library = sorted(st.session_state.library, key=lambda x: x['title'].lower())
    elif sort_option == "Title (Z-A)":
        sorted_library = sorted(st.session_state.library, key=lambda x: x['title'].lower(), reverse=True)
    elif sort_option == "Author (A-Z)":
        sorted_library = sorted(st.session_state.library, key=lambda x: x['author'].lower())
    elif sort_option == "Author (Z-A)":
        sorted_library = sorted(st.session_state.library, key=lambda x: x['author'].lower(), reverse=True)
    elif sort_option == "Year (Newest)":
        sorted_library = sorted(st.session_state.library, key=lambda x: x['year'], reverse=True)
    elif sort_option == "Year (Oldest)":
        sorted_library = sorted(st.session_state.library, key=lambda x: x['year'])
    
    display_book_list(sorted_library)
    
    if st.button("Back to Menu"):
        st.session_state.current_view = "menu"
        st.rerun()

def display_book_list(books):
    """Display a formatted list of books with expandable details."""
    for book in books:
        with st.expander(f"{book['title']} by {book['author']}"):
            read_status = "✓" if book['read'] else "✗"
            st.write(f"**Title:** {book['title']}")
            st.write(f"**Author:** {book['author']}")
            st.write(f"**Year:** {book['year']}")
            st.write(f"**Genre:** {book['genre']}")
            st.write(f"**Read:** {read_status}")

def statistics_view():
    """Show library statistics with charts."""
    st.title("Library Statistics")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        if st.button("Back to Menu"):
            st.session_state.current_view = "menu"
            st.rerun()
        return
    
    total_books = len(st.session_state.library)
    read_count = sum(1 for book in st.session_state.library if book['read'])
    percentage_read = (read_count / total_books) * 100 if total_books > 0 else 0
    
    st.metric("Total books", total_books)
    st.metric("Books read", f"{read_count} ({percentage_read:.1f}%)")
    
    # Genre distribution chart
    genres = {}
    for book in st.session_state.library:
        genre = book['genre'] if book['genre'] else "Unknown"
        genres[genre] = genres.get(genre, 0) + 1
    
    if genres:
        st.subheader("Genre Distribution")
        st.bar_chart(genres)  # Visualize genres
    
    # Read status chart
    read_status = {
        "Read": read_count,
        "Unread": total_books - read_count
    }
    st.subheader("Read Status")
    st.bar_chart(read_status)  # Visualize read/unread
    
    if st.button("Back to Menu"):
        st.session_state.current_view = "menu"
        st.rerun()

def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()  # Set up initial state
    
    # Navigation based on current view
    if st.session_state.current_view == "menu":
        display_menu()
    elif st.session_state.current_view == "add_book":
        add_book_view()
    elif st.session_state.current_view == "remove_book":
        remove_book_view()
    elif st.session_state.current_view == "search_books":
        search_books_view()
    elif st.session_state.current_view == "view_all":
        view_all_books()
    elif st.session_state.current_view == "statistics":
        statistics_view()

if __name__ == "__main__":
    main()  # Run the app