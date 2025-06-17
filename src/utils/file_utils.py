"""
File handling utilities for e-book processing
"""
import unicodedata
import re

def sanitize_string(input_str):
    """
    Sanitize string for use in filenames
    Converts special characters to ASCII and replaces non-alphanumeric with underscores
    """
    # Normalize the string to decompose special characters
    normalized_str = unicodedata.normalize('NFKD', input_str)
    # Encode to ASCII bytes, ignoring errors, then decode back to string
    ascii_str = normalized_str.encode('ASCII', 'ignore').decode('ASCII')
    # Replace any non-alphanumeric characters with underscores
    sanitized_str = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_str)
    # Remove leading and trailing underscores
    sanitized_str = sanitized_str.strip('_')
    return sanitized_str

def create_ebook_filename(author_name, book_title, year):
    """
    Create a standardized filename for e-book downloads
    Format: Author-Title[Year].kepub.epub
    """
    # Sanitize each component
    sanitized_author = sanitize_string(author_name)
    sanitized_title = sanitize_string(book_title)
    # Format the filename
    filename = f"{sanitized_author}-{sanitized_title}[{year}].kepub.epub"
    return filename