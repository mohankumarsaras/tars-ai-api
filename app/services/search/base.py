from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class SearchProvider(ABC):
    @abstractmethod
    def index(self, entity_id: int, entity_type: str, title: str, content: str, verification_status: str = "VERIFIED", source: Optional[str] = None):
        """Index a document for searching."""
        pass
        
    @abstractmethod
    def delete(self, entity_id: int, entity_type: str):
        """Remove a document from the search index."""
        pass
        
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search across all indexed documents."""
        pass
