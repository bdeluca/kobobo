import base64

import requests
import xml.etree.ElementTree as ET


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
        return f"({self.name}, {self.items} books)"

    def __repr__(self):
        return self.__str__()

    def __init__(self, name, items, url):
        self.name = name
        self.items = items
        self.url = url
        self.encoded_name = base64.urlsafe_b64encode(name.encode()).decode()





def fetch_opds_feed(url):
    c = Config()

    response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password))
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f'Failed to retrieve OPDS feed: {response.status_code}')

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
