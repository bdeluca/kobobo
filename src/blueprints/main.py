"""
Main blueprint for core routes (index, book details)
"""
from flask import Blueprint, render_template, abort
from calibre.cache import GlobalCache

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with recent books"""
    recent_books = GlobalCache().get_catalog("Newest")
    recent_books = recent_books.books
    return render_template('index.html', recent_books=recent_books[:9])

@main_bp.route('/book/<string:book_id>')
def book_detail(book_id):
    """Individual book detail page"""
    book = GlobalCache().get_book(book_id)
    if not book:
        abort(404, description="Book not found")
    return render_template('book.html', book=book)

@main_bp.route('/binfo')
def binfo():
    """Browser information debug page"""
    from flask import request, render_template_string
    user_agent = request.headers.get('User-Agent')
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Browser Information</title>
        </head>
        <body>
            <h1>Browser Information</h1>
            <p>User Agent: {{ user_agent }}</p>
        </body>
        </html>
    ''', user_agent=user_agent)