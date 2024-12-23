import re
from collections import OrderedDict
from datetime import datetime
from urllib.parse import quote_plus, urlparse

import requests
import xml.etree.ElementTree as ET
from typing import Optional

from calibre.cache import GlobalCache
from config import Config
from requests.auth import HTTPDigestAuth


def search_opds(search_terms, library_id='calibre'):
    """
    """
    # URL-encode the search terms
    encoded_search_terms = quote_plus(search_terms)

    # Construct the search URL
    search_url = f"/opds/search/{encoded_search_terms}?library_id={library_id}"
    response = fetch_opds_feed(search_url)
    if response == "No Books Found":
        return []
    return Book.retrieve_books(response)

class Catalog:
    @classmethod
    def create_catalog(cls, name, url):
        cat = Catalog
        if name == "Authors":
            from calibre.authors import AuthorsCatalog
            cat = AuthorsCatalog
        elif name == "Title":
            cat = TitleCatalog
        elif name == "Newest":
            cat = NewestCatalog

        return cat(name, url)


    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.letters = set()

class TitleCatalog(Catalog):
    def gather(self):
        page = fetch_opds_feed(self.url)
        books = Book.retrieve_books(page)
        GlobalCache().series = OrderedDict(sorted(GlobalCache().series.items()))
        return books

class NewestCatalog(Catalog):

    def __init__(self, name, url):
        super().__init__(name, url)
        self.books = []

    def gather(self):
        page = fetch_opds_feed(self.url)
        self.books =  Book.retrieve_books(page, onepage=True)

class Book:
    series_re = re.compile(
    r'^(?P<series_name>.*?)\s*\[(?P<series_position>\d+)\]$'
)

    @classmethod
    def retrieve_books(cls, page, onepage=False):
        import xml.etree.ElementTree as ET
        # Load and parse the XML file
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "dc": "http://purl.org/dc/terms/",
            "opds": "http://opds-spec.org/2010/catalog",
            "xhtml": "http://www.w3.org/1999/xhtml"
        }

        # Parse the XML data
        root = ET.fromstring(page)

        books = []
        next_url = None
        for entry in root.findall("atom:entry", ns):
            namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
            for link in root.findall('atom:link', namespaces):
                if link.get('rel') == 'next':
                    next_url = link.get('href')
                    break
            title = entry.find("atom:title", ns).text
            author = entry.find("atom:author/atom:name", ns).text
            id_ = entry.find("atom:id", ns).text
            published_date = entry.find("dc:date", ns).text if entry.find("dc:date",
                                                                          ns) is not None else datetime.today().isoformat()

            # Extract content and parse for tags, series, and description
            content = entry.find("atom:content", ns)
            description = None
            tags = None
            series = None
            rating = None
            if content is not None:
                content_div = content.find("xhtml:div", ns)
                if content_div is not None:
                    # Convert all text in the content to lines
                    content_lines = "".join(content_div.itertext()).split("\n")

                    # Extract tags
                    for line in content_lines:
                        if line.startswith("TAGS:"):
                            tags = line[len("TAGS:"):].strip()
                        if line.startswith("SERIES:"):
                            series = line[len("SERIES:"):].strip()

                    # Extract all <p> tags for the description
                    paragraphs = content_div.findall("xhtml:p", ns)
                    if paragraphs:
                        raw_description = "\n\n".join("".join(p.itertext()).strip() for p in paragraphs)
                        description = "\n".join(line.strip() for line in raw_description.splitlines() if line.strip())

                    # Extract rating
                    rating_start = "".join(content_div.itertext()).find("RATING: ")
                    if rating_start != -1:
                        rating = "".join(content_div.itertext())[rating_start + 8:].split("\n")[0].strip()

                # Extract links
            if rating is None:
                rating = ""

            epub_link = None
            cover_image = None
            cover_id = None
            for link in entry.findall("atom:link", ns):
                rel = link.get("rel")
                if rel == "http://opds-spec.org/acquisition" and link.get("type") == "application/epub+zip":
                    epub_link = link.get("href")
                elif rel == "http://opds-spec.org/cover":
                    cover_image = link.get("href")
                    parsed_url = urlparse(cover_image)
                    path_segments = parsed_url.path.split('/')
                    cover_id = path_segments[3] if len(path_segments) > 3 else None

            # Create a Book object and add it to the list
            book = cls(
                title=title,
                author=author,
                id=id_,
                published_date=published_date,
                description=description,
                tags=tags,
                series=series,
                epub_link=epub_link,
                cover_image=cover_image,
                cover_id=cover_id,
                rating=rating
            )

            GlobalCache().set_book(book.id, book)
            books.append(book)
        if next_url is not None and not onepage:
            page = fetch_opds_feed(next_url)
            books += cls.retrieve_books(page)
        return books



    def __init__(self, title: str, author: str, id: str, published_date: Optional[str], description: Optional[str], tags: Optional[str], series: Optional[str], epub_link: Optional[str], cover_image: Optional[str], cover_id: Optional[str], rating: Optional[str]):
        self.title = title
        self.author = author
        self.id = id
        self.published_date = datetime.fromisoformat(published_date)
        self.year = self.published_date.year
        self.pretty_date = self.published_date.strftime("%x")
        self.description = description
        self.tags = tags
        self.series = series
        self.epub_link = epub_link
        self.cover_image = cover_image
        self.rating = rating
        self.cover_id = cover_id
        if self.series:
            match = self.series_re.search(self.series)
            if match:
                series_name = match.group('series_name').strip()
                series_position = int(match.group('series_position'))
                GlobalCache().set_series(series_name, series_position, self)


    def __repr__(self):
        return f"Book(title={self.title}, author={self.author}, id={self.id})"


def fetch_opds_feed(url):
    c = Config()
    response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password))
    return response.text


def parse_opds_catalogs():
    catalog_feed = fetch_opds_feed("opds")
    root = ET.fromstring(catalog_feed)
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

    search_link = root.find('atom:link[@rel="search"]', namespaces)

    # Extract the href attribute
    if search_link is not None:
        search_href = search_link.get('href')
        GlobalCache().set_catalog('search', search_href)
    entries = []
    for entry in root.findall('atom:entry', namespaces):
        # Find the 'title' element within the current 'entry'
        title_element = entry.find('atom:title', namespaces)
        # Find the 'link' element within the current 'entry'
        link_element = entry.find('atom:link', namespaces)

        # Extract the text of the 'title' element
        title = title_element.text if title_element is not None else None
        title = title.replace("By ", "")
        # Extract the 'href' attribute of the 'link' element
        href = link_element.get('href') if link_element is not None else None

        # Append the extracted data as a dictionary to the entries list
        entries.append({'title': title, 'href': href})
        c = Catalog.create_catalog(title, href)
        if title not in ["Library", "Publisher", "Series"]:
            GlobalCache().set_catalog(title, c)


def gather_catalogs():
    c = Config()
    print(f"Connecting to {c.opds_url_root}")
    parse_opds_catalogs()
    GlobalCache().get_catalog('Authors').gather()
    GlobalCache().get_catalog('Title').gather()
    GlobalCache().get_catalog('Newest').gather()
    print("Done gathering catalogs")


def test():
    gather_catalogs()
    print(type(GlobalCache().series))
    for series in GlobalCache().series:
        sd = GlobalCache().get_series(series)
        print(f"{series} - {next(iter(sd.values())).author}")
        for position, book in sorted(sd.items()):
            print(f"    {position}: {sd[position].title}")



if __name__ == '__main__':
    test()

    #c = GlobalCache().get_catalog('Title')
    # books = c.gather()
    # for book in books:
    #     print(book.title)
    #


