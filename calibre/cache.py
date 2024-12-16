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
