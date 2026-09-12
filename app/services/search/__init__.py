from .base import SearchProvider
from .sqlite_provider import SQLiteSearchProvider

def get_search_provider(db) -> SearchProvider:
    return SQLiteSearchProvider(db)
