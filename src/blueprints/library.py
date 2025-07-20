"""
Library blueprint for authors and series browsing
"""
import base64
from flask import Blueprint, render_template
from calibre.cache import GlobalCache
import calibre.opds as opds
from config import Config
from utils.sorting import get_grouping_letter

library_bp = Blueprint('library', __name__)

@library_bp.route('/authors')
def authors():
    """Authors listing organized alphabetically"""
    authors_catalog = GlobalCache().get_catalog("Authors")
    author_dict = authors_catalog.authors
    letter_dict = {}
    
    for author in author_dict.values():
        initial = author.name[0].upper()
        if initial not in letter_dict:
            letter_dict[initial] = []
        letter_dict[initial].append(author)
    
    letters = sorted(letter_dict.keys())
    return render_template('authors.html', letter_dict=letter_dict, letters=letters)

@library_bp.route('/series')
def series():
    """Series listing organized alphabetically"""
    series_dict = GlobalCache().series
    letter_dict = {}
    
    for series_title in series_dict.keys():
        initial = get_grouping_letter(series_title)
        if initial not in letter_dict:
            letter_dict[initial] = []
        letter_dict[initial].append(series_title)
    
    letters = sorted(letter_dict.keys())
    return render_template('series.html', letter_dict=letter_dict, letters=letters, series=series_dict)

@library_bp.route('/author/<string:encoded_id>')
def author_page(encoded_id):
    """Individual author page"""
    # Decode the Base64-encoded ID
    decoded_id = base64.b64decode(encoded_id).decode('utf-8')
    
    opds.gather_catalogs()
    authors_catalog = GlobalCache().get_catalog("Authors")
    authors_catalog.gather()
    author_dict = authors_catalog.authors
    author = author_dict.get(decoded_id)
    
    if author:
        author.gather()
    
    c = Config()
    calibre_root = c.opds_url_root
    return render_template('author.html', author=author, calibre_root=calibre_root)