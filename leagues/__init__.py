import db
import importlib
import inspect
import sqlite3

class DbContext():
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        db.conn = sqlite3.connect(self.db_name)
        db.conn.row_factory = sqlite3.Row

    def __exit__(self, *args):
        db.conn.close()
        db.conn = None

class DomainContext():
    _current_context = None

    @staticmethod
    def current():
        if DomainContext._current_context == None:
            raise Exception('league_context is null')
        return DomainContext._current_context

    def __init__(self, domain_name):
        self.domain_name = domain_name

    def _load_module(self, file_name):
        return importlib.import_module('leagues.%s.%s' % (self.domain_name, file_name))

    def __enter__(self):
        if DomainContext._current_context != None:
            raise Exception('league_context is already set')
        DomainContext._current_context = self

        self.scraping = self._load_module('scraping')
        self.domain = self._load_module('domain')
        self.scraping.install_cache()

    def __exit__(self, *args):
        self.scraping = None
        self.domain = None
        DomainContext._current_context = None

class LeagueContext():
    def __init__(self, league_name):
        self.league_name = league_name
        self._db_context = DbContext(self.league_name + '.db')
        self._domain_context = DomainContext(self.league_name)

    def __enter__(self):
        self._db_context.__enter__()
        self._domain_context.__enter__()

    def __exit__(self, *args):
        self._db_context.__exit__()
        self._domain_context.__exit__()
