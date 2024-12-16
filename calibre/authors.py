import base64
from collections import OrderedDict

from calibre.opds import Catalog, fetch_opds_feed, Book


class AuthorsCatalog(Catalog):

    def __init__(self, name, url):
        super().__init__(name, url)
        self.authors = {}

    def gather(self):
        page = fetch_opds_feed(self.url)

        import xml.etree.ElementTree as ET
        # Load and parse the XML file
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # Parse the XML data
        root = ET.fromstring(page)

        # Initialize a list to store author information


        # Iterate over each 'entry' element
        for entry in root.findall('atom:entry', ns):
            # Extract the author's name from the 'title' element
            author_name = entry.find('atom:title', ns).text

            # Extract the number of books from the 'content' element
            content_text = entry.find('atom:content', ns).text
            if 'one book' in content_text:
                book_count = 1
            else:
                # Extract the number from the content text (e.g., '6 books')
                book_count = int(content_text.split()[0])
            link = entry.find('atom:link', ns).get('href')

            # Append the author and book count to the list
            self.authors[author_name] = (Author(author_name, book_count, link))
        new_authors = OrderedDict()

        for x in sorted(self.authors.keys()):
            new_authors[x] = self.authors[x]
        self.authors = new_authors


class Author:
    def __str__(self):
        return f"Author: {self.name}, {self.items} books"

    def __repr__(self):
        return self.__str__()

    def __init__(self, name, items, url):
        self.name = name
        self.items = items
        self.url = url
        self.encoded_name = base64.urlsafe_b64encode(name.encode()).decode()
        self.books = []

    def gather(self):
        page = fetch_opds_feed(self.url)
        self.books = Book.retrieve_books(page)


