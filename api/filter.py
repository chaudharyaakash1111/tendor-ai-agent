"""
Filter and ranking logic for tenders.
"""
from typing import List, Dict, Any
from datetime import datetime
from db.models import Tender

def filter_tenders(tenders: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """
    Filter tenders based on provided criteria.
    
    Args:
        tenders: List of tender dictionaries
        filters: Dictionary containing filter criteria
        
    Returns:
        Filtered list of tenders
    """
    filtered = tenders
    
    # Filter by organization
    if "organization" in filters:
        org_filter = filters["organization"].lower()
        filtered = [t for t in filtered if org_filter in t["organization"].lower()]
    
    # Filter by category
    if "category" in filters:
        cat_filter = filters["category"].lower()
        filtered = [t for t in filtered if cat_filter in t["category"].lower()]
    
    # Filter by location
    if "location" in filters:
        loc_filter = filters["location"].lower()
        filtered = [t for t in filtered if loc_filter in t["location"].lower()]
    
    # Filter by value range
    if "min_value" in filters:
        min_val = float(filters["min_value"])
        filtered = [t for t in filtered if t["value"] >= min_val]
    
    if "max_value" in filters:
        max_val = float(filters["max_value"])
        filtered = [t for t in filtered if t["value"] <= max_val]
    
    # Filter by deadline
    if "deadline_from" in filters:
        try:
            deadline_from = datetime.fromisoformat(filters["deadline_from"])
            filtered = [t for t in filtered if datetime.fromisoformat(t["deadline"]) >= deadline_from]
        except ValueError:
            pass  # Invalid date format, skip filter
    
    if "deadline_to" in filters:
        try:
            deadline_to = datetime.fromisoformat(filters["deadline_to"])
            filtered = [t for t in filtered if datetime.fromisoformat(t["deadline"]) <= deadline_to]
        except ValueError:
            pass  # Invalid date format, skip filter
    
    return filtered

def rank_tenders(tenders: List[Dict], query: str = "") -> List[Dict]:
    """
    Rank tenders by deadline (soonest first) and optionally by keyword match.
    
    Args:
        tenders: List of tender dictionaries
        query: Optional search query for keyword matching
        
    Returns:
        Ranked list of tenders
    """
    # Sort by deadline (soonest first)
    # Handle both string and datetime objects
    def get_deadline(tender):
        deadline = tender["deadline"]
        if isinstance(deadline, str):
            return datetime.fromisoformat(deadline)
        return deadline
    
    ranked = sorted(tenders, key=get_deadline)
    
    # If query provided, rank by keyword match
    if query:
        query_words = query.lower().split()
        
        def keyword_score(tender):
            score = 0
            text = f"{tender['organization']} {tender['category']} {tender['location']} {tender['description']}".lower()
            for word in query_words:
                if word in text:
                    score += 1
            return score
        
        # Sort by keyword score (higher first), then by deadline
        ranked = sorted(ranked, key=lambda t: (-keyword_score(t), get_deadline(t)))
    
    return ranked