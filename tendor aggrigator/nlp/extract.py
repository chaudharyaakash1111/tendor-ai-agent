"""
NLP processing for tender data extraction and normalization.
"""
import re
from datetime import datetime
from typing import List, Dict
import spacy
from dateutil import parser

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
    nlp = None

class Tender:
    def __init__(self, tender_id: str, organization: str, category: str, location: str, 
                 value: float, deadline: datetime, description: str, link: str):
        self.tender_id = tender_id
        self.organization = organization
        self.category = category
        self.location = location
        self.value = value
        self.deadline = deadline
        self.description = description
        self.link = link
    
    def dict(self):
        return {
            "tender_id": self.tender_id,
            "organization": self.organization,
            "category": self.category,
            "location": self.location,
            "value": self.value,
            "deadline": self.deadline,
            "description": self.description,
            "link": self.link
        }

def extract_tender_id(text: str) -> str:
    """Extract tender ID using regex patterns."""
    # Common tender ID patterns
    patterns = [
        r'[A-Z]{2,}-\d{4}-\d{3}',  # ET-2025-001
        r'[A-Z]{3,}\d{2,}',        # GEM2025001
        r'\d{4}/[A-Z]{2,}/\d{2}'   # 2025/ET/01
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return "UNKNOWN"

def extract_value(text: str) -> float:
    """Extract monetary value from text."""
    # Pattern for ₹ currency values
    rupee_pattern = r'[₹$]\s*([\d,]+\.?\d*)'
    match = re.search(rupee_pattern, text)
    
    if match:
        value_str = match.group(1).replace(',', '')
        try:
            return float(value_str)
        except ValueError:
            pass
    
    # Pattern for plain numbers (last resort)
    number_pattern = r'(\d+\.?\d*)'
    match = re.search(number_pattern, text)
    
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    
    return 0.0

def extract_deadline(text: str) -> datetime:
    """Extract deadline date from text."""
    try:
        # Try to parse with dateutil
        return parser.parse(text, dayfirst=True)
    except:
        # Default to a future date if parsing fails
        return datetime(2025, 12, 31)

def extract_organization(text: str) -> str:
    """Extract organization using spaCy NER."""
    if not nlp:
        return text[:100]  # Return first 100 characters as fallback
    
    doc = nlp(text)
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    
    if orgs:
        return orgs[0]
    
    return text[:100]

def extract_location(text: str) -> str:
    """Extract location using spaCy NER."""
    if not nlp:
        # Simple extraction of common Indian cities as fallback
        cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", 
                  "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur"]
        
        for city in cities:
            if city.lower() in text.lower():
                return city
        
        return "India"
    
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    
    if locations:
        return locations[0]
    
    return "India"

def process_tenders(raw_tenders: List[Dict]) -> List[Tender]:
    """Process raw tender data and normalize it."""
    processed_tenders = []
    
    for tender in raw_tenders:
        # Extract and normalize fields
        tender_id = extract_tender_id(tender.get("tender_id", "") + " " + tender.get("description", ""))
        organization = extract_organization(tender.get("organization", "") + " " + tender.get("description", ""))
        category = tender.get("category", "General")
        location = extract_location(tender.get("location", "") + " " + tender.get("description", ""))
        value = extract_value(tender.get("value", "0"))
        deadline = extract_deadline(tender.get("deadline", "2025-12-31"))
        description = tender.get("description", "")
        link = tender.get("link", "")
        
        # Create processed tender object
        processed_tender = Tender(
            tender_id=tender_id,
            organization=organization,
            category=category,
            location=location,
            value=value,
            deadline=deadline,
            description=description,
            link=link
        )
        
        processed_tenders.append(processed_tender)
    
    return processed_tenders