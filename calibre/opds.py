import base64
import os.path
from datetime import datetime, timezone

import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from collections import OrderedDict
from config import Config
from requests.auth import HTTPDigestAuth



GLOBAL_DATA = {}

class Catalog:
    @classmethod
    def create_catalog(cls, name, url):
        cname = f"{name.lower().title()}Catalog"
        x = globals().get(cname)
        if x is None:
            x = Catalog
        return x(name, url)



    def __init__(self, name, url):
        self.name = name

        self.url = url
        self.letters = set()


class AuthorsCatalog(Catalog):

    def __init__(self, name, url):
        super().__init__(name, url)
        self.authors = {}

    def gather(self):
        page = fetch_opds_feed(self.url)

        import xml.etree.ElementTree as ET
        from collections import defaultdict
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
            published_date = entry.find("dc:date", ns).text if entry.find("dc:date", ns) is not None else datetime.today().isoformat()

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
                    from os.path import dirname, join, exists  #what a mess, maybe I should just be serving the dynamically, but thats a pain, quick and dirty, really dirty
                    cover_url =  join("covers", id_ + ".jpg")
                    cover_url = cover_url.replace("urn:uuid:", "")
                    local_cover = join(dirname(dirname(__file__)), join("static", cover_url))
                    if not exists(local_cover):
                        download_fom_opds_feed(cover_image, local_cover)
                    cover_image = cover_url
                    cover_image = cover_image.replace("\\", "/")


            # Create a Book object and add it to the list
            book = Book(
                title=title,
                author=author,
                id=id_,
                published_date=published_date,
                description=description,
                tags=tags,
                series=series,
                epub_link=epub_link,
                cover_image=cover_image,
                rating = rating
            )
            books.append(book)
        self.books = sorted(books, key=lambda bk: bk.published_date, reverse=True)

class Book:
    def __init__(self, title: str, author: str, id: str, published_date: Optional[str], description: Optional[str], tags: Optional[str], series: Optional[str], epub_link: Optional[str], cover_image: Optional[str], rating: Optional[str]):
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

    def __repr__(self):
        return f"Book(title={self.title}, author={self.author}, id={self.id})"


def fetch_opds_feed(url):
    c = Config()

    response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password))
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f'Failed to retrieve OPDS feed: {response.status_code}')

def download_fom_opds_feed(url, target):
    c = Config()
    try:
        response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password), stream=True)
        response.raise_for_status()
        with open(target, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("saved to", target)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def parse_opds_catalogs():
    catalog_feed = fetch_opds_feed("opds")
    root = ET.fromstring(catalog_feed)
    entries = []
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
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
            GLOBAL_DATA[title] = c


def gather_catalogs():
    parse_opds_catalogs()
    cat = GLOBAL_DATA['Authors']
    cat.gather()



if __name__ == '__main__':
    gather_catalogs()
    aus = GLOBAL_DATA['Authors']
    aus.gather()
    a = list(aus.authors.values())[1]

    a.gather()
    for b in a.books:
         print(b.title)
    #     print(b.cover_image)
         print(b.description)
         print("--------")
    #     print(b.published_date)
    #      print(b.series)
    #     #print(b.rating)


