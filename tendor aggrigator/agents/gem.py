"""
Scraping agent for GeM portal (https://gem.gov.in)
"""
import requests
from bs4 import BeautifulSoup
import time

def scrape_gem():
    """
    Scrape tenders from GeM portal.
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://gem.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data
        sample_tenders = [
            {
                "tender_id": "GEM-2025-001",
                "organization": "Department of Defence",
                "category": "Electronics",
                "location": "Pune",
                "value": "₹1,00,00,000",
                "deadline": "2025-10-05",
                "description": "Procurement of communication equipment for military use",
                "link": "https://gem.gov.in/tenders/GEM-2025-001"
            },
            {
                "tender_id": "GEM-2025-002",
                "organization": "Ministry of Health",
                "category": "Medical Equipment",
                "location": "Delhi",
                "value": "₹5,00,00,000",
                "deadline": "2025-11-10",
                "description": "Supply of ICU medical devices to government hospitals",
                "link": "https://gem.gov.in/tenders/GEM-2025-002"
            },
            {
                "tender_id": "GEM-2025-003",
                "organization": "Department of Education",
                "category": "Furniture",
                "location": "Bangalore",
                "value": "₹75,00,000",
                "deadline": "2025-09-25",
                "description": "Supply of laboratory furniture for schools",
                "link": "https://gem.gov.in/tenders/GEM-2025-003"
            },
            {
                "tender_id": "GEM-2025-004",
                "organization": "Indian Space Research Organisation",
                "category": "Scientific Equipment",
                "location": "Ahmedabad",
                "value": "₹25,00,00,000",
                "deadline": "2025-12-01",
                "description": "Calibration equipment for satellite testing facility",
                "link": "https://gem.gov.in/tenders/GEM-2025-004"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping GeM: {e}")
    
    return tenders