from datetime import datetime
from urllib.parse import quote_plus, urlparse

import requests
import xml.etree.ElementTree as ET
from typing import Optional
from config import Config
from requests.auth import HTTPDigestAuth


class GlobalCache:
    _instance = None  # Class variable to hold the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalCache, cls).__new__(cls)
            cls._instance.catalogs = {}  # Initialize catalogs dictionary
            cls._instance.books = {}     # Initialize books dictionary
        return cls._instance

    def get_catalog(self, key):
        return self.catalogs.get(key)

    def set_catalog(self, key, value):
        self.catalogs[key] = value

    def get_book(self, key):
        return self.books.get(key)

    def set_book(self, key, value):
        self.books[key] = value

    def clear_catalogs(self):
        self.catalogs.clear()

    def clear_books(self):
        self.books.clear()

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
        print(name)
        cat = Catalog
        if name == "Authors":
            from calibre.authors import AuthorsCatalog
            cat = AuthorsCatalog
        return cat(name, url)


    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.letters = set()


class Book:
    @classmethod
    def retrieve_books(cls, page):
        import xml.etree.ElementTree as ET
        from collections import defaultdict
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

        for entry in root.findall("atom:entry", ns):

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
            books.append(book)

        return books



    def __init__(self, title: str, author: str, id: str, published_date: Optional[str], description: Optional[str], tags: Optional[str], series: Optional[str], epub_link: Optional[str], cover_image: Optional[str], cover_id: Optional[str], rating: Optional[str]):
        self.title = title
        self.author = author
        self.id = id
        self.published_date = published_date
        self.description = description
        self.tags = tags
        self.series = series
        self.epub_link = epub_link
        self.cover_image = cover_image
        self.rating = rating
        self.cover_id = cover_id

    def __repr__(self):
        return f"Book(title={self.title}, author={self.author}, id={self.id})"


def fetch_opds_feed(url):
    c = Config()
    response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password))
    return response.text

# def download_fom_opds_feed(url, target):
#     c = Config()
#     try:
#         response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password), stream=True)
#         response.raise_for_status()
#         with open(target, 'wb') as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         print("saved to", target)
#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")


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
        if title not in ["Library", "Publisher"]:
            GlobalCache().set_catalog(title, c)


def gather_catalogs():
    parse_opds_catalogs()
    cat = GlobalCache().get_catalog('Authors')
    cat.gather()



if __name__ == '__main__':
    gather_catalogs()
    aus = GlobalCache().get_catalog('Authors')
    aus.gather()
    a = list(aus.authors.values())[1]
    a.gather()
    for b in a.books:
         print(b.title)
    # #      print(b.cover_id)
    # #      # print(b.description)
    # #      print("--------")
    # #     print(b.published_date)
    # #      print(b.series)
    # #     #print(b.rating)
    #
    #
    # print(GLOBAL_DATA['search'])
    # x = search_opds('brass man')
    # for b in x:
    #     print(b.title)
