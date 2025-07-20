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
    # Get all books from cache
    all_books = []
    for book_id, book in GlobalCache().books.items():
        all_books.append(book)
    
    # Sort by title, ignoring articles like "The", "A", "An"
    all_books.sort(key=lambda x: get_sort_key(x.title))
    
    # Return all books - JavaScript will handle pagination
    return render_template('books.html', books=all_books, total_books=len(all_books))

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