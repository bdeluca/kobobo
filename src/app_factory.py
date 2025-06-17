"""
Flask application factory for Kobobo
"""
import logging
from flask import Flask, render_template

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from blueprints.main import main_bp
    from blueprints.books import books_bp
    from blueprints.library import library_bp
    from blueprints.downloads import downloads_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(downloads_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', 
                             message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', 
                             message="Internal server error"), 500
    
    # Debug routes (only in development)
    if app.debug:
        @app.route('/debug/series')
        def debug_series():
            from flask import render_template_string
            from calibre.cache import GlobalCache
            
            series_dict = GlobalCache().series
            debug_info = []
            
            for series_name, books in list(series_dict.items())[:10]:
                book_info = []
                for position, book in sorted(books.items()):
                    book_info.append(f"Position {position}: {book.title}")
                debug_info.append({
                    'series_name': series_name,
                    'books': book_info
                })
            
            return render_template_string('''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Series Debug</title>
                </head>
                <body>
                    <h1>Series Debug Information</h1>
                    <p>Total series: {{ total_series }}</p>
                    {% for series in debug_info %}
                    <h3>{{ series.series_name }}</h3>
                    <ul>
                    {% for book in series.books %}
                        <li>{{ book }}</li>
                    {% endfor %}
                    </ul>
                    {% endfor %}
                </body>
                </html>
            ''', debug_info=debug_info, total_series=len(series_dict))
    
    return app