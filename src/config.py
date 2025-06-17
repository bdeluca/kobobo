import os
import configparser


class Config:
    _instance = None  # Class-level instance variable for singleton

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_dir="config", config_file="settings.ini"):
        if not hasattr(self, "_initialized"):
            self.config_dir = config_dir
            self._initialized = True
            self.config_file = config_file
            self.config_path = os.path.join(self.config_dir, self.config_file)
            self._config = configparser.ConfigParser()

            # Load the configuration file
            self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        self._config.read(self.config_path)

    def get(self, section, option, fallback=None):
        """
        Retrieve a value from the config file.

        :param section: Section in the config file
        :param option: Option name within the section
        :param fallback: Default value if the option is missing
        :return: Value from the config file or fallback if not found
        """
        return self._config.get(section, option, fallback=fallback)

    @property
    def opds_url_root(self):
        return self.get("OPDS", "URL_ROOT")

    @property
    def username(self):
        return self.get("OPDS", "USERNAME")

    @property
    def password(self):
        return self.get("OPDS", "PASSWORD")

    @property
    def kepubify(self):
        return self.get("CONVERTER", "KEPUBIFY")