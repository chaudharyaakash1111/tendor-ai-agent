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
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "GEM-2025-001",
                "title": "Procurement of communication equipment for military use",
                "organization": "Department of Defence",
                "location": "Pune",
                "deadline": "2025-10-05",
                "value": "₹1,00,00,000",
                "source": "GeM"
            },
            {
                "tender_id": "GEM-2025-002",
                "title": "Supply of ICU medical devices to government hospitals",
                "organization": "Ministry of Health",
                "location": "Delhi",
                "deadline": "2025-11-10",
                "value": "₹5,00,00,000",
                "source": "GeM"
            },
            {
                "tender_id": "GEM-2025-003",
                "title": "Supply of laboratory furniture for schools",
                "organization": "Department of Education",
                "location": "Bangalore",
                "deadline": "2025-09-25",
                "value": "₹75,00,000",
                "source": "GeM"
            },
            {
                "tender_id": "GEM-2025-004",
                "title": "Calibration equipment for satellite testing facility",
                "organization": "Indian Space Research Organisation",
                "location": "Ahmedabad",
                "deadline": "2025-12-01",
                "value": "₹25,00,00,000",
                "source": "GeM"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping GeM: {e}")
    
    return tenders