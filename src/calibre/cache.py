from typing import OrderedDict


class GlobalCache:
    _instance = None  # Class variable to hold the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalCache, cls).__new__(cls)
            cls._instance.catalogs = {}  # Initialize catalogs dictionary
            cls._instance.books = {}     # Initialize books dictionary
            cls._instance.series = OrderedDict()
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

    def set_series(self, key, position, book):
        if key not in self.series.keys():
            self.series[key] = {}
        self.series[key][position] = book

    def get_series(self, key):
        return self.series.get(key)

    def clear_series(self):
        self.series.clear()