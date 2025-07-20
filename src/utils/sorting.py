"""
Sorting utilities for handling book titles and series names
"""

# Common English articles to ignore when sorting
ARTICLES = ('the', 'a', 'an')

def get_sort_key(title):
    """
    Returns a sort key for a title, removing leading articles.
    
    Examples:
        "The Martian" -> "martian"
        "A Game of Thrones" -> "game of thrones"
        "An Unexpected Journey" -> "unexpected journey"
        "Foundation" -> "foundation"
    """
    if not title:
        return ""
    
    # Convert to lowercase for comparison
    title_lower = title.lower().strip()
    
    # Check if title starts with any article
    for article in ARTICLES:
        if title_lower.startswith(article + ' '):
            # Remove the article and the space after it
            return title_lower[len(article) + 1:].strip()
    
    return title_lower


def get_grouping_letter(title):
    """
    Returns the first letter for alphabetical grouping, ignoring articles.
    
    Examples:
        "The Martian" -> "M"
        "A Game of Thrones" -> "G"
        "An Unexpected Journey" -> "U"
        "Foundation" -> "F"
    """
    sort_key = get_sort_key(title)
    
    if sort_key:
        return sort_key[0].upper()
    
    # Fallback if title is empty or only contains an article
    return '#'