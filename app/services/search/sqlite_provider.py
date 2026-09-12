from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base import SearchProvider

class SQLiteSearchProvider(SearchProvider):
    def __init__(self, db: Session):
        self.db = db
        
    def index(self, entity_id: int, entity_type: str, title: str, content: str, verification_status: str = "VERIFIED", source: Optional[str] = None):
        # First remove if it exists to handle updates
        self.delete(entity_id, entity_type)
        
        query = text("""
            INSERT INTO global_search (entity_id, entity_type, title, content, verification_status, source)
            VALUES (:entity_id, :entity_type, :title, :content, :verification_status, :source)
        """)
        self.db.execute(query, {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "title": title,
            "content": content,
            "verification_status": verification_status,
            "source": source
        })
        # Note: Caller is responsible for db.commit()
        
    def delete(self, entity_id: int, entity_type: str):
        query = text("""
            DELETE FROM global_search 
            WHERE entity_id = :entity_id AND entity_type = :entity_type
        """)
        self.db.execute(query, {
            "entity_id": entity_id,
            "entity_type": entity_type
        })
        
    def search(self, query_str: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Using bm25 ranking for relevance
        query = text("""
            SELECT entity_id, entity_type, title, content, verification_status, source, bm25(global_search) as rank
            FROM global_search 
            WHERE global_search MATCH :query
            ORDER BY rank
            LIMIT :limit
        """)
        
        # In FTS5, BM25 rank is lower = better (more relevant)
        
        # Format the query for FTS5 (very basic sanitization to avoid syntax errors)
        safe_query = query_str.replace('"', '').replace("'", "")
        
        result = self.db.execute(query, {"query": safe_query, "limit": limit})
        
        results = []
        for row in result:
            results.append({
                "entity_id": row.entity_id,
                "category": row.entity_type,
                "result": row.title,
                "snippet": row.content[:150] + "..." if len(row.content) > 150 else row.content,
                "source": row.source,
                "verification_status": row.verification_status,
                "relevance": abs(row.rank)  # absolute value to make it positive, just as a generic score
            })
            
        return results
