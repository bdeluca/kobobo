"""
Books blueprint for book browsing and search functionality
"""
from flask import Blueprint, render_template, request
from calibre.cache import GlobalCache
from calibre.opds import search_opds
from utils.sorting import get_sort_key

books_bp = Blueprint('books', __name__)

@books_bp.route('/books')
def books():
    """All books listing with pagination"""
    # Get page number from query params
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    
    # Get all books from cache
    all_books = []
    for book_id, book in GlobalCache().books.items():
        all_books.append(book)
    
    # Sort by title, ignoring articles like "The", "A", "An"
    all_books.sort(key=lambda x: get_sort_key(x.title))
    
    # Pagination
    books_per_page = 48  # Divisible by 3 for our grid layout
    total_books = len(all_books)
    total_pages = (total_books + books_per_page - 1) // books_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page > total_pages:
        page = total_pages
    
    # Calculate slice indices
    start_idx = (page - 1) * books_per_page
    end_idx = start_idx + books_per_page
    books_to_show = all_books[start_idx:end_idx]
    
    return render_template('books.html', 
                         books=books_to_show, 
                         total_books=total_books,
                         current_page=page,
                         total_pages=total_pages,
                         books_per_page=books_per_page)

@books_bp.route('/ratings')
def ratings():
    """Books organized by rating"""
    rating_dict = {}
    
    for book_id, book in GlobalCache().books.items():
        rating = book.rating if book.rating else "No Rating"
        if rating not in rating_dict:
            rating_dict[rating] = []
        rating_dict[rating].append(book)
    
    # Sort ratings (5 stars to 1 star, then no rating)
    sorted_ratings = []
    for i in range(5, 0, -1):
        star_rating = "★" * i
        if star_rating in rating_dict:
            # Sort books within each rating group, ignoring articles
            rating_dict[star_rating].sort(key=lambda x: get_sort_key(x.title))
            sorted_ratings.append((star_rating, rating_dict[star_rating]))
    
    if "No Rating" in rating_dict:
        # Sort books in the "No Rating" group as well
        rating_dict["No Rating"].sort(key=lambda x: get_sort_key(x.title))
        sorted_ratings.append(("No Rating", rating_dict["No Rating"]))
    
    return render_template('ratings.html', rating_groups=sorted_ratings)

@books_bp.route('/language')
def language():
    """Language filtering (placeholder)"""
    return render_template('language.html', 
                         message="Language filtering not yet available from OPDS data")

@books_bp.route('/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        try:
            results = search_opds(query)
        except Exception as e:
            print(f"Search error: {e}")
            results = []
    
    return render_template('search.html', query=query, results=results)