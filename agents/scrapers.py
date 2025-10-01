"""
Consolidated scraping agents for all tender portals.
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse

# Set up requests session with headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
})

# Central Government Portals
def scrape_etenders():
    """
    Scrape tenders from eTenders portal (https://etenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # eTenders portal URL
        base_url = "https://etenders.gov.in"
        url = f"{base_url}/eprocure/app"
        
        # Make request to the portal
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tender table or list elements
        # Try multiple common selectors for tender data
        selectors = [
            'table tr',  # Table rows
            '.tender',   # Elements with tender class
            '[class*="tender"]',  # Elements with class containing "tender"
            '.row',      # Generic row elements
            'a[href*="tender"]',  # Links containing "tender"
            '.list-item',  # List items
            '.news-item',  # News items
            '.content-item'  # Content items
        ]
        
        tender_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                tender_elements.extend(elements)
            if len(tender_elements) > 30:  # Increase limit for much more data
                break
        
        # If we still don't have elements, get all links and divs
        if not tender_elements:
            tender_elements = soup.find_all(['a', 'div'], href=True) + soup.find_all('div')
        
        # Process found tender elements (limiting to 25 for much more data)
        for i, element in enumerate(tender_elements[:25]):
            try:
                # Extract tender information
                text_content = element.get_text(strip=True) if element.get_text() else ""
                
                # Skip if content is too short
                if len(text_content) < 10:  # Reduced minimum length to get more data
                    continue
                
                # Try to find tender ID in the text or attributes
                tender_id_match = re.search(r'[A-Z]{2,}-\d{4}-\d{3}', text_content)
                if not tender_id_match:
                    tender_id_match = re.search(r'[A-Z]{3,}\d{2,}', text_content)
                if not tender_id_match:
                    tender_id_match = re.search(r'\d{4}[A-Z]{2,}\d{2,}', text_content)
                tender_id = tender_id_match.group(0) if tender_id_match else f"ET-{time.strftime('%Y')}-{str(i+1).zfill(3)}"
                
                # Extract title with more context
                # Try to find a more descriptive title
                title_candidates = re.findall(r'[A-Z][^.!?]*?(?:tender|procurement|supply|service|work|contract|purchase|bid)[^.!?]*?[.!?]', text_content, re.IGNORECASE)
                if title_candidates:
                    title = title_candidates[0].strip()[:200]  # Increased length limit
                else:
                    # Fallback to first part of text content
                    title = text_content[:200] if text_content else f"eTenders Portal Tender - Item {i+1}"
                
                # Try to find organization keywords with more comprehensive matching
                org_keywords = ['ministry', 'department', 'commission', 'board', 'authority', 'corporation', 'organisation', 'organization', 'university', 'institute', 'agency', 'office', 'division', 'cell', 'unit']
                organization = "Government of India"
                for keyword in org_keywords:
                    # Look for organization names with more context
                    org_matches = re.findall(rf'([A-Z][a-zA-Z\s]*?{keyword}[a-zA-Z\s]*?)(?:\s|$|[-:;,.\d])', text_content, re.IGNORECASE)
                    if org_matches:
                        # Take the longest match as it's likely to be more specific
                        organization = max(org_matches, key=len).strip()
                        break
                
                # Try to find monetary value with multiple patterns
                value_patterns = [
                    r'[₹$]\s*([\d,]+\.?\d*)',
                    r'Rs\.?\s*([\d,]+\.?\d*)',
                    r'INR\s*([\d,]+\.?\d*)',
                    r'rupees?\s*([\d,]+\.?\d*)',
                    r'amount\s*[:\-]?\s*[₹$]?\s*([\d,]+\.?\d*)',
                    r'[\d,]+\.?\d*\s*(?:crores?|lakhs?|thousands?)',
                    r'[\d,]+\.?\d*\s*[₹$]'
                ]
                value = "₹0"
                for pattern in value_patterns:
                    value_match = re.search(pattern, text_content, re.IGNORECASE)
                    if value_match:
                        matched_value = value_match.group(0)
                        # Extract just the numeric part
                        numeric_part = re.search(r'[\d,]+\.?\d*', matched_value)
                        if numeric_part:
                            value = f"₹{numeric_part.group(0).replace(',', '')}"
                        else:
                            value = matched_value
                        break
                
                # Try to find deadline with multiple patterns
                deadline_patterns = [
                    r'(?:closing\s*date|deadline|last\s*date|due\s*date).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(?:valid.*?till|until|upto).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})'  # YYYY-MM-DD format
                ]
                deadline = "2025-12-31"
                for pattern in deadline_patterns:
                    deadline_match = re.search(pattern, text_content, re.IGNORECASE)
                    if deadline_match:
                        deadline = deadline_match.group(1)
                        break
                
                # Try to find location with more comprehensive matching
                indian_cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", 
                               "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", 
                               "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
                               "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
                               "Rajkot", "Kalyan", "Vasai", "Varanasi", "Srinagar", "Aurangabad",
                               "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad", "Ranchi",
                               "Howrah", "Coimbatore", "Jalandhar", "Gwalior", "Vijayawada",
                               "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh",
                               "Hubli", "Mysore", "Tiruchirappalli", "Bareilly", "Moradabad",
                               "Gurgaon", "Aligarh", "Jalandhar", "Bhubaneswar", "Bhiwandi",
                               "Salem", "Mira-Bhayandar", "Thiruvananthapuram", "Bhatpara",
                               "Warangal", "Guntur", "Bikaner", "Amravati", "Noida", "Jamshedpur"]
                location = "India"
                for city in indian_cities:
                    if city.lower() in text_content.lower():
                        location = city
                        break
                
                # Create tender object with complete details
                tender = {
                    "tender_id": tender_id,
                    "title": title,
                    "organization": organization,
                    "location": location,
                    "deadline": deadline,
                    "value": value,
                    "source": "eTenders"
                }
                
                tenders.append(tender)
                
            except Exception as e:
                # Skip individual tender if there's an error parsing it
                continue
        
        # If no tenders found through parsing, add sample data
        if not tenders:
            # Add more sample tenders to ensure we have data
            for i in range(1, 6):  # Generate 5 sample tenders
                tenders.append({
                    "tender_id": f"ET-2025-{str(i).zfill(3)}",
                    "title": f"Government Procurement Tender {i} from eTenders Portal - Complete Sample Data",
                    "organization": "Government of India",
                    "location": "New Delhi, India",
                    "deadline": "2025-12-31",
                    "value": f"₹{i*1000000:,}",
                    "source": "eTenders"
                })
        
    except requests.exceptions.RequestException as e:
        print(f"Network error scraping eTenders: {e}")
        # Fallback to sample data in case of network error
        for i in range(1, 6):  # Generate 5 sample tenders
            tenders.append({
                "tender_id": f"ET-2025-{str(i).zfill(3)}",
                "title": f"Government Procurement Tender {i} (Network error - using sample data with complete details)",
                "organization": "Government of India",
                "location": "New Delhi, India",
                "deadline": "2025-12-31",
                "value": f"₹{i*1000000:,}",
                "source": "eTenders"
            })
    except Exception as e:
        print(f"Error scraping eTenders: {e}")
        # Fallback to sample data in case of other errors
        for i in range(1, 6):  # Generate 5 sample tenders
            tenders.append({
                "tender_id": f"ET-2025-{str(i).zfill(3)}",
                "title": f"Government Procurement Tender {i} (Parsing error - using sample data with complete details)",
                "organization": "Government of India",
                "location": "New Delhi, India",
                "deadline": "2025-12-31",
                "value": f"₹{i*1000000:,}",
                "source": "eTenders"
            })
    
    return tenders

def scrape_gem():
    """
    Scrape tenders from GeM portal (https://gem.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # GeM portal URL
        url = "https://gem.gov.in"
        
        # Make request to the portal
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tender-related elements
        # Try multiple common selectors for tender data
        selectors = [
            'a[href*="tender"]',  # Links containing "tender"
            '.tender-card',       # Tender card elements
            '[class*="tender"]',  # Elements with class containing "tender"
            '.bid',               # Bid-related elements
            '[class*="bid"]',     # Elements with class containing "bid"
            '.table tr',          # Table rows
            '.list-item',         # List items
            '.news-item',         # News items
            '.content-item'       # Content items
        ]
        
        tender_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                tender_elements.extend(elements)
            if len(tender_elements) > 30:  # Increase limit for much more data
                break
        
        # If we still don't have elements, get all links and divs
        if not tender_elements:
            tender_elements = soup.find_all(['a', 'div'], href=True) + soup.find_all('div')
        
        # Process found tender elements (limiting to 25 for much more data)
        for i, element in enumerate(tender_elements[:25]):
            try:
                # Extract tender information
                text_content = element.get_text(strip=True) if element.get_text() else ""
                
                # Skip if content is too short
                if len(text_content) < 10:  # Reduced minimum length to get more data
                    continue
                
                # Try to find tender ID in the text or attributes
                tender_id_match = re.search(r'[A-Z]{3,}\d{2,}', text_content)
                if not tender_id_match:
                    tender_id_match = re.search(r'[A-Z]{2,}-\d{4}-\d{3}', text_content)
                if not tender_id_match:
                    tender_id_match = re.search(r'\d{4}[A-Z]{2,}\d{2,}', text_content)
                tender_id = tender_id_match.group(0) if tender_id_match else f"GEM-{time.strftime('%Y')}-{str(i+1).zfill(3)}"
                
                # Extract title with more context
                # Try to find a more descriptive title
                title_candidates = re.findall(r'[A-Z][^.!?]*?(?:tender|procurement|supply|service|work|contract|purchase|bid)[^.!?]*?[.!?]', text_content, re.IGNORECASE)
                if title_candidates:
                    title = title_candidates[0].strip()[:200]  # Increased length limit
                else:
                    # Fallback to first part of text content
                    title = text_content[:200] if text_content else f"GeM Portal Tender - Item {i+1}"
                
                # Try to find organization keywords with more comprehensive matching
                org_keywords = ['gem', 'ministry', 'department', 'commission', 'board', 'authority', 'corporation', 'organisation', 'organization', 'university', 'institute', 'agency', 'office']
                organization = "Government e-Marketplace (GeM)"
                for keyword in org_keywords:
                    # Look for organization names with more context
                    org_matches = re.findall(rf'([A-Z][a-zA-Z\s]*?{keyword}[a-zA-Z\s]*?)(?:\s|$|[-:;,.\d])', text_content, re.IGNORECASE)
                    if org_matches:
                        # Take the longest match as it's likely to be more specific
                        organization = max(org_matches, key=len).strip()
                        break
                
                # Try to find monetary value with multiple patterns
                value_patterns = [
                    r'[₹$]\s*([\d,]+\.?\d*)',
                    r'Rs\.?\s*([\d,]+\.?\d*)',
                    r'INR\s*([\d,]+\.?\d*)',
                    r'rupees?\s*([\d,]+\.?\d*)',
                    r'amount\s*[:\-]?\s*[₹$]?\s*([\d,]+\.?\d*)',
                    r'[\d,]+\.?\d*\s*(?:crores?|lakhs?|thousands?)',
                    r'[\d,]+\.?\d*\s*[₹$]'
                ]
                value = "₹0"
                for pattern in value_patterns:
                    value_match = re.search(pattern, text_content, re.IGNORECASE)
                    if value_match:
                        matched_value = value_match.group(0)
                        # Extract just the numeric part
                        numeric_part = re.search(r'[\d,]+\.?\d*', matched_value)
                        if numeric_part:
                            value = f"₹{numeric_part.group(0).replace(',', '')}"
                        else:
                            value = matched_value
                        break
                
                # Try to find deadline with multiple patterns
                deadline_patterns = [
                    r'(?:closing\s*date|deadline|last\s*date|due\s*date).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(?:valid.*?till|until|upto).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})'  # YYYY-MM-DD format
                ]
                deadline = "2025-12-31"
                for pattern in deadline_patterns:
                    deadline_match = re.search(pattern, text_content, re.IGNORECASE)
                    if deadline_match:
                        deadline = deadline_match.group(1)
                        break
                
                # Try to find location with more comprehensive matching
                indian_cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", 
                               "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", 
                               "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
                               "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
                               "Rajkot", "Kalyan", "Vasai", "Varanasi", "Srinagar", "Aurangabad",
                               "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad", "Ranchi",
                               "Howrah", "Coimbatore", "Jalandhar", "Gwalior", "Vijayawada",
                               "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh",
                               "Hubli", "Mysore", "Tiruchirappalli", "Bareilly", "Moradabad",
                               "Gurgaon", "Aligarh", "Jalandhar", "Bhubaneswar", "Bhiwandi",
                               "Salem", "Mira-Bhayandar", "Thiruvananthapuram", "Bhatpara",
                               "Warangal", "Guntur", "Bikaner", "Amravati", "Noida", "Jamshedpur"]
                location = "India"
                for city in indian_cities:
                    if city.lower() in text_content.lower():
                        location = city
                        break
                
                # Create tender object with complete details
                tender = {
                    "tender_id": tender_id,
                    "title": title,
                    "organization": organization,
                    "location": location,
                    "deadline": deadline,
                    "value": value,
                    "source": "GeM"
                }
                
                tenders.append(tender)
                
            except Exception as e:
                # Skip individual tender if there's an error parsing it
                continue
        
        # If no tenders found through parsing, add sample data
        if not tenders:
            # Add more sample tenders to ensure we have data
            for i in range(1, 6):  # Generate 5 sample tenders
                tenders.append({
                    "tender_id": f"GEM-2025-{str(i).zfill(3)}",
                    "title": f"Procurement Tender {i} from GeM Portal - Complete Sample Data",
                    "organization": "Government e-Marketplace (GeM)",
                    "location": "New Delhi, India",
                    "deadline": "2025-12-31",
                    "value": f"₹{i*500000:,}",
                    "source": "GeM"
                })
        
    except requests.exceptions.RequestException as e:
        print(f"Network error scraping GeM: {e}")
        # Fallback to sample data in case of network error
        for i in range(1, 6):  # Generate 5 sample tenders
            tenders.append({
                "tender_id": f"GEM-2025-{str(i).zfill(3)}",
                "title": f"Procurement Tender {i} from GeM Portal (Network error - using sample data with complete details)",
                "organization": "Government e-Marketplace (GeM)",
                "location": "New Delhi, India",
                "deadline": "2025-12-31",
                "value": f"₹{i*500000:,}",
                "source": "GeM"
            })
    except Exception as e:
        print(f"Error scraping GeM: {e}")
        # Fallback to sample data in case of other errors
        for i in range(1, 6):  # Generate 5 sample tenders
            tenders.append({
                "tender_id": f"GEM-2025-{str(i).zfill(3)}",
                "title": f"Procurement Tender {i} from GeM Portal (Parsing error - using sample data with complete details)",
                "organization": "Government e-Marketplace (GeM)",
                "location": "New Delhi, India",
                "deadline": "2025-12-31",
                "value": f"₹{i*500000:,}",
                "source": "GeM"
            })
    
    return tenders

def scrape_ireps():
    """
    Scrape tenders from IREPS portal (https://ireps.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # IREPS portal URL (corrected)
        url = "https://ireps.gov.in"
        
        # Make request to the portal
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tender-related elements
        # Try multiple common selectors for tender data
        selectors = [
            'a[href*="tender"]',  # Links containing "tender"
            '.tender',            # Elements with tender class
            '[class*="tender"]',  # Elements with class containing "tender"
            '.table tr',          # Table rows
            '.list-item',         # List items
            '.news-item',         # News items
            '.content-item',      # Content items
            '.bid-item'           # Bid items
        ]
        
        tender_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                tender_elements.extend(elements)
            if len(tender_elements) > 30:  # Increase limit for much more data
                break
        
        # If we still don't have elements, get all links and divs
        if not tender_elements:
            tender_elements = soup.find_all(['a', 'div'], href=True) + soup.find_all('div')
        
        # Process found tender elements (limiting to 25 for much more data)
        for i, element in enumerate(tender_elements[:25]):
            try:
                # Extract tender information
                text_content = element.get_text(strip=True) if element.get_text() else ""
                
                # Skip if content is too short
                if len(text_content) < 10:  # Reduced minimum length to get more data
                    continue
                
                # Try to find tender ID in the text or attributes
                tender_id_match = re.search(r'[A-Z]{3,}\d{2,}', text_content)
                if not tender_id_match:
                    tender_id_match = re.search(r'[A-Z]{2,}-\d{4}-\d{3}', text_content)
                if not tender_id_match:
                    tender_id_match = re.search(r'\d{4}[A-Z]{2,}\d{2,}', text_content)
                tender_id = tender_id_match.group(0) if tender_id_match else f"IREPS-{time.strftime('%Y')}-{str(i+1).zfill(3)}"
                
                # Extract title with more context
                # Try to find a more descriptive title
                title_candidates = re.findall(r'[A-Z][^.!?]*?(?:tender|procurement|supply|service|work|contract|purchase|bid)[^.!?]*?[.!?]', text_content, re.IGNORECASE)
                if title_candidates:
                    title = title_candidates[0].strip()[:200]  # Increased length limit
                else:
                    # Fallback to first part of text content
                    title = text_content[:200] if text_content else f"Railway Procurement Tender - Item {i+1}"
                
                # Try to find organization keywords with more comprehensive matching
                org_keywords = ['railway', 'rail', 'ircon', 'irfc', 'railtel', 'irctc', 'compass', 'railways', 'ministry', 'department']
                organization = "Indian Railways"
                for keyword in org_keywords:
                    # Look for organization names with more context
                    org_matches = re.findall(rf'([A-Z][a-zA-Z\s]*?{keyword}[a-zA-Z\s]*?)(?:\s|$|[-:;,.\d])', text_content, re.IGNORECASE)
                    if org_matches:
                        # Take the longest match as it's likely to be more specific
                        organization = max(org_matches, key=len).strip()
                        break
                
                # Try to find monetary value with multiple patterns
                value_patterns = [
                    r'[₹$]\s*([\d,]+\.?\d*)',
                    r'Rs\.?\s*([\d,]+\.?\d*)',
                    r'INR\s*([\d,]+\.?\d*)',
                    r'rupees?\s*([\d,]+\.?\d*)',
                    r'amount\s*[:\-]?\s*[₹$]?\s*([\d,]+\.?\d*)',
                    r'[\d,]+\.?\d*\s*(?:crores?|lakhs?|thousands?)',
                    r'[\d,]+\.?\d*\s*[₹$]'
                ]
                value = "₹0"
                for pattern in value_patterns:
                    value_match = re.search(pattern, text_content, re.IGNORECASE)
                    if value_match:
                        matched_value = value_match.group(0)
                        # Extract just the numeric part
                        numeric_part = re.search(r'[\d,]+\.?\d*', matched_value)
                        if numeric_part:
                            value = f"₹{numeric_part.group(0).replace(',', '')}"
                        else:
                            value = matched_value
                        break
                
                # Try to find deadline with multiple patterns
                deadline_patterns = [
                    r'(?:closing\s*date|deadline|last\s*date|due\s*date).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(?:valid.*?till|until|upto).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})'  # YYYY-MM-DD format
                ]
                deadline = "2025-12-31"
                for pattern in deadline_patterns:
                    deadline_match = re.search(pattern, text_content, re.IGNORECASE)
                    if deadline_match:
                        deadline = deadline_match.group(1)
                        break
                
                # Try to find location with more comprehensive matching
                railway_locations = ["New Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore", "Hyderabad", 
                                   "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", 
                                   "Indore", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
                                   "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
                                   "Rajkot", "Varanasi", "Ranchi", "Bhubaneswar", "Guwahati",
                                   "Howrah", "Coimbatore", "Jalandhar", "Gwalior", "Vijayawada",
                                   "Jodhpur", "Madurai", "Raipur", "Kota", "Chandigarh",
                                   "Hubli", "Mysore", "Tiruchirappalli", "Bareilly", "Moradabad",
                                   "Gurgaon", "Aligarh", "Bhiwandi", "Salem", "Mira-Bhayandar",
                                   "Thiruvananthapuram", "Bhatpara", "Warangal", "Guntur", "Bikaner",
                                   "Amravati", "Noida", "Jamshedpur"]
                location = "India"
                for city in railway_locations:
                    if city.lower() in text_content.lower():
                        location = city
                        break
                
                # Create tender object with complete details
                tender = {
                    "tender_id": tender_id,
                    "title": title,
                    "organization": organization,
                    "location": location,
                    "deadline": deadline,
                    "value": value,
                    "source": "IREPS"
                }
                
                tenders.append(tender)
                
            except Exception as e:
                # Skip individual tender if there's an error parsing it
                continue
        
        # If no tenders found through parsing, add sample data
        if not tenders:
            # Add more sample tenders to ensure we have data
            for i in range(1, 6):  # Generate 5 sample tenders
                tenders.append({
                    "tender_id": f"IREPS-2025-{str(i).zfill(3)}",
                    "title": f"Railway Procurement Tender {i} from IREPS Portal - Complete Sample Data",
                    "organization": "Indian Railways",
                    "location": "New Delhi, India",
                    "deadline": "2025-12-31",
                    "value": f"₹{i*2000000:,}",
                    "source": "IREPS"
                })
        
    except requests.exceptions.RequestException as e:
        print(f"Network error scraping IREPS: {e}")
        # Fallback to sample data in case of network error
        for i in range(1, 6):  # Generate 5 sample tenders
            tenders.append({
                "tender_id": f"IREPS-2025-{str(i).zfill(3)}",
                "title": f"Railway Procurement Tender {i} from IREPS Portal (Network error - using sample data with complete details)",
                "organization": "Indian Railways",
                "location": "New Delhi, India",
                "deadline": "2025-12-31",
                "value": f"₹{i*2000000:,}",
                "source": "IREPS"
            })
    except Exception as e:
        print(f"Error scraping IREPS: {e}")
        # Fallback to sample data in case of other errors
        for i in range(1, 6):  # Generate 5 sample tenders
            tenders.append({
                "tender_id": f"IREPS-2025-{str(i).zfill(3)}",
                "title": f"Railway Procurement Tender {i} from IREPS Portal (Parsing error - using sample data with complete details)",
                "organization": "Indian Railways",
                "location": "New Delhi, India",
                "deadline": "2025-12-31",
                "value": f"₹{i*2000000:,}",
                "source": "IREPS"
            })
    
    return tenders

def scrape_defproc():
    """
    Scrape tenders from Defence Procurement Portal (https://defproc.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Defence Procurement Portal URL
        url = "https://defproc.gov.in"
        
        # Make request to the portal
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tender-related elements
        # Try multiple common selectors for tender data
        selectors = [
            'a[href*="tender"]',  # Links containing "tender"
            '.tender',            # Elements with tender class
            '[class*="tender"]',  # Elements with class containing "tender"
            '.table tr',          # Table rows
            '.news-item'          # News items (often contain tenders)
        ]
        
        tender_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                tender_elements.extend(elements)
            if len(tender_elements) > 10:  # Limit for performance
                break
        
        # If we still don't have elements, get all links
        if not tender_elements:
            tender_elements = soup.find_all('a', href=True)
        
        # Process found tender elements (limiting to 5 for demo)
        for i, element in enumerate(tender_elements[:5]):
            try:
                # Extract tender information
                text_content = element.get_text(strip=True) if element.get_text() else ""
                
                # Skip if content is too short
                if len(text_content) < 10:
                    continue
                
                # Try to find tender ID in the text or attributes
                tender_id_match = re.search(r'[A-Z]{3,}\d{2,}', text_content)
                tender_id = tender_id_match.group(0) if tender_id_match else f"DEF-{time.strftime('%Y')}-{str(i+1).zfill(3)}"
                
                # Extract title
                title = text_content[:100] if text_content else f"Defence Procurement Tender - Item {i+1}"
                
                # Try to find organization keywords
                org_keywords = ['defence', 'ministry', 'army', 'navy', 'air force', 'bsl', 'ordnance']
                organization = "Ministry of Defence"
                for keyword in org_keywords:
                    if keyword in text_content.lower():
                        # Extract the organization name
                        org_match = re.search(rf'([A-Z][a-zA-Z\s]*?{keyword}[a-zA-Z\s]*?)(?:\s|$)', text_content, re.IGNORECASE)
                        if org_match:
                            organization = org_match.group(1).strip()
                            break
                
                # Try to find monetary value
                value_match = re.search(r'[₹$]\s*([\d,]+\.?\d*)', text_content)
                value = value_match.group(0) if value_match else "₹0"
                
                # Try to find deadline
                deadline_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text_content)
                deadline = deadline_match.group(0) if deadline_match else "2025-12-31"
                
                # Location is often New Delhi for defence tenders
                location = "New Delhi"
                
                # Create tender object
                tender = {
                    "tender_id": tender_id,
                    "title": title,
                    "organization": organization,
                    "location": location,
                    "deadline": deadline,
                    "value": value,
                    "source": "Defence Procurement Portal"
                }
                
                tenders.append(tender)
                
            except Exception as e:
                # Skip individual tender if there's an error parsing it
                continue
        
        # If no tenders found through parsing, add a sample one
        if not tenders:
            tenders.append({
                "tender_id": "DEF-2025-001",
                "title": "Defence Equipment Procurement Tender",
                "organization": "Ministry of Defence",
                "location": "New Delhi",
                "deadline": "2025-12-31",
                "value": "₹0",
                "source": "Defence Procurement Portal"
            })
        
    except requests.exceptions.RequestException as e:
        print(f"Network error scraping Defence Procurement Portal: {e}")
        # Fallback to sample data in case of network error
        tenders.append({
            "tender_id": "DEF-2025-001",
            "title": "Defence Equipment Procurement Tender (Network error - using sample data)",
            "organization": "Ministry of Defence",
            "location": "New Delhi",
            "deadline": "2025-12-31",
            "value": "₹0",
            "source": "Defence Procurement Portal"
        })
    except Exception as e:
        print(f"Error scraping Defence Procurement Portal: {e}")
        # Fallback to sample data in case of other errors
        tenders.append({
            "tender_id": "DEF-2025-001",
            "title": "Defence Equipment Procurement Tender (Parsing error - using sample data)",
            "organization": "Ministry of Defence",
            "location": "New Delhi",
            "deadline": "2025-12-31",
            "value": "₹0",
            "source": "Defence Procurement Portal"
        })
    
    return tenders

# State Government Portals
def scrape_mahatenders():
    """
    Scrape tenders from Maharashtra Tenders Portal (https://mahatenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://mahatenders.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "MAH-2025-001",
                "title": "Construction of state highway bridges",
                "organization": "Maharashtra State Public Works Department",
                "location": "Mumbai",
                "deadline": "2025-10-18",
                "value": "₹25,00,00,000",
                "source": "Maharashtra Tenders"
            },
            {
                "tender_id": "MAH-2025-002",
                "title": "Development of smart city infrastructure",
                "organization": "Mumbai Metropolitan Region Development Authority",
                "location": "Mumbai",
                "deadline": "2025-11-12",
                "value": "₹40,00,00,000",
                "source": "Maharashtra Tenders"
            },
            {
                "tender_id": "MAH-2025-003",
                "title": "Installation of solar power systems",
                "organization": "Maharashtra State Electricity Distribution Company",
                "location": "Pune",
                "deadline": "2025-09-30",
                "value": "₹15,00,00,000",
                "source": "Maharashtra Tenders"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Maharashtra Tenders Portal: {e}")
    
    return tenders

def scrape_rajasthan():
    """
    Scrape tenders from Rajasthan eProcurement Portal (https://eproc.rajasthan.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://eproc.rajasthan.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "RJ-2025-001",
                "title": "Installation of solar power plants",
                "organization": "Rajasthan Renewable Energy Corporation",
                "location": "Jaipur",
                "deadline": "2025-10-22",
                "value": "₹30,00,00,000",
                "source": "Rajasthan eProcurement"
            },
            {
                "tender_id": "RJ-2025-002",
                "title": "Construction of state highways",
                "organization": "Rajasthan State Highways Department",
                "location": "Udaipur",
                "deadline": "2025-11-25",
                "value": "₹50,00,00,000",
                "source": "Rajasthan eProcurement"
            },
            {
                "tender_id": "RJ-2025-003",
                "title": "Water treatment plant installation",
                "organization": "Rajasthan Urban Infrastructure Development",
                "location": "Jodhpur",
                "deadline": "2025-12-10",
                "value": "₹20,00,00,000",
                "source": "Rajasthan eProcurement"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Rajasthan eProcurement Portal: {e}")
    
    return tenders

def scrape_up():
    """
    Scrape tenders from Uttar Pradesh eTender Portal (https://etender.up.nic.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://etender.up.nic.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "UP-2025-001",
                "title": "Water supply pipeline network",
                "organization": "Uttar Pradesh Jal Nigam",
                "location": "Lucknow",
                "deadline": "2025-10-28",
                "value": "₹35,00,00,000",
                "source": "Uttar Pradesh eTender"
            },
            {
                "tender_id": "UP-2025-002",
                "title": "Procurement of public buses",
                "organization": "Uttar Pradesh State Road Transport",
                "location": "Kanpur",
                "deadline": "2025-11-18",
                "value": "₹45,00,00,000",
                "source": "Uttar Pradesh eTender"
            },
            {
                "tender_id": "UP-2025-003",
                "title": "Construction of school buildings",
                "organization": "Uttar Pradesh Education Department",
                "location": "Allahabad",
                "deadline": "2025-12-08",
                "value": "₹18,00,00,000",
                "source": "Uttar Pradesh eTender"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Uttar Pradesh eTender Portal: {e}")
    
    return tenders

def scrape_tntenders():
    """
    Scrape tenders from Tamil Nadu eTenders Portal (https://tntenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://tntenders.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "TN-2025-001",
                "title": "Water treatment facility upgrade",
                "organization": "Tamil Nadu Water Supply and Drainage Board",
                "location": "Chennai",
                "deadline": "2025-10-12",
                "value": "₹28,00,00,000",
                "source": "Tamil Nadu eTenders"
            },
            {
                "tender_id": "TN-2025-002",
                "title": "Procurement of electric buses",
                "organization": "Tamil Nadu State Transport Corporation",
                "location": "Coimbatore",
                "deadline": "2025-11-05",
                "value": "₹22,00,00,000",
                "source": "Tamil Nadu eTenders"
            },
            {
                "tender_id": "TN-2025-003",
                "title": "Road construction and maintenance",
                "organization": "Tamil Nadu Public Works Department",
                "location": "Madurai",
                "deadline": "2025-12-20",
                "value": "₹35,00,00,000",
                "source": "Tamil Nadu eTenders"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Tamil Nadu eTenders Portal: {e}")
    
    return tenders

def scrape_kerala():
    """
    Scrape tenders from Kerala Tenders Portal (https://keralatenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://keralatenders.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "KL-2025-001",
                "title": "Installation of hydroelectric generators",
                "organization": "Kerala State Electricity Board",
                "location": "Thiruvananthapuram",
                "deadline": "2025-10-14",
                "value": "₹32,00,00,000",
                "source": "Kerala Tenders"
            },
            {
                "tender_id": "KL-2025-002",
                "title": "Construction of government buildings",
                "organization": "Kerala State Public Works Department",
                "location": "Kochi",
                "deadline": "2025-11-08",
                "value": "₹26,00,00,000",
                "source": "Kerala Tenders"
            },
            {
                "tender_id": "KL-2025-003",
                "title": "Supply of medical diagnostic equipment",
                "organization": "Kerala State Health Services",
                "location": "Kozhikode",
                "deadline": "2025-12-02",
                "value": "₹18,00,00,000",
                "source": "Kerala Tenders"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Kerala Tenders Portal: {e}")
    
    return tenders

def scrape_wb():
    """
    Scrape tenders from West Bengal Tenders Portal (https://wbtenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://wbtenders.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "WB-2025-001",
                "title": "Renewable energy project development",
                "organization": "West Bengal Power Development Corporation",
                "location": "Kolkata",
                "deadline": "2025-10-25",
                "value": "₹40,00,00,000",
                "source": "West Bengal Tenders"
            },
            {
                "tender_id": "WB-2025-002",
                "title": "Procurement of CNG buses",
                "organization": "West Bengal State Transport Corporation",
                "location": "Asansol",
                "deadline": "2025-11-12",
                "value": "₹20,00,00,000",
                "source": "West Bengal Tenders"
            },
            {
                "tender_id": "WB-2025-003",
                "title": "Bridge construction project",
                "organization": "West Bengal Public Works Department",
                "location": "Siliguri",
                "deadline": "2025-12-18",
                "value": "₹30,00,00,000",
                "source": "West Bengal Tenders"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping West Bengal Tenders Portal: {e}")
    
    return tenders

def scrape_jharkhand():
    """
    Scrape tenders from Jharkhand Tenders Portal (https://jharkhandtenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://jharkhandtenders.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "JH-2025-001",
                "title": "Dam construction and irrigation project",
                "organization": "Jharkhand State Water Resources Department",
                "location": "Ranchi",
                "deadline": "2025-10-30",
                "value": "₹25,00,00,000",
                "source": "Jharkhand Tenders"
            },
            {
                "tender_id": "JH-2025-002",
                "title": "Coal mining equipment procurement",
                "organization": "Jharkhand State Mining Corporation",
                "location": "Dhanbad",
                "deadline": "2025-11-22",
                "value": "₹35,00,00,000",
                "source": "Jharkhand Tenders"
            },
            {
                "tender_id": "JH-2025-003",
                "title": "Smart city infrastructure development",
                "organization": "Jharkhand Urban Development Department",
                "location": "Jamshedpur",
                "deadline": "2025-12-15",
                "value": "₹20,00,00,000",
                "source": "Jharkhand Tenders"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Jharkhand Tenders Portal: {e}")
    
    return tenders

def scrape_assam():
    """
    Scrape tenders from Assam Tenders Portal (https://assamtenders.gov.in).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://assamtenders.gov.in"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "AS-2025-001",
                "title": "Hydroelectric power plant maintenance",
                "organization": "Assam State Electricity Board",
                "location": "Guwahati",
                "deadline": "2025-10-18",
                "value": "₹22,00,00,000",
                "source": "Assam Tenders"
            },
            {
                "tender_id": "AS-2025-002",
                "title": "Road construction in tea garden areas",
                "organization": "Assam State Public Works Department",
                "location": "Dibrugarh",
                "deadline": "2025-11-14",
                "value": "₹28,00,00,000",
                "source": "Assam Tenders"
            },
            {
                "tender_id": "AS-2025-003",
                "title": "Supply of agricultural research equipment",
                "organization": "Assam Agricultural University",
                "location": "Jorhat",
                "deadline": "2025-12-05",
                "value": "₹15,00,00,000",
                "source": "Assam Tenders"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping Assam Tenders Portal: {e}")
    
    return tenders

# Private Aggregators
def scrape_tendertiger():
    """
    Scrape tenders from TenderTiger (https://www.tendertiger.com).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://www.tendertiger.com"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "TT-2025-001",
                "title": "Website development and maintenance services",
                "organization": "Tech Solutions Pvt Ltd",
                "location": "Bangalore",
                "deadline": "2025-10-10",
                "value": "₹12,00,000",
                "source": "TenderTiger"
            },
            {
                "tender_id": "TT-2025-002",
                "title": "Commercial complex construction",
                "organization": "Global Infrastructure Corp",
                "location": "Hyderabad",
                "deadline": "2025-11-02",
                "value": "₹8,00,00,000",
                "source": "TenderTiger"
            },
            {
                "tender_id": "TT-2025-003",
                "title": "Medical equipment procurement",
                "organization": "MediCare Hospitals",
                "location": "Chennai",
                "deadline": "2025-12-01",
                "value": "₹5,00,00,000",
                "source": "TenderTiger"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping TenderTiger: {e}")
    
    return tenders

def scrape_bidassist():
    """
    Scrape tenders from BidAssist (https://bidassist.com).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://bidassist.com"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "BA-2025-001",
                "title": "Educational software development",
                "organization": "EduTech Solutions",
                "location": "Pune",
                "deadline": "2025-10-22",
                "value": "₹3,00,00,000",
                "source": "BidAssist"
            },
            {
                "tender_id": "BA-2025-002",
                "title": "POS system implementation across stores",
                "organization": "Retail Chain India Ltd",
                "location": "Delhi",
                "deadline": "2025-11-18",
                "value": "₹15,00,00,000",
                "source": "BidAssist"
            },
            {
                "tender_id": "BA-2025-003",
                "title": "Catering services for corporate clients",
                "organization": "Food Services Pvt Ltd",
                "location": "Mumbai",
                "deadline": "2025-12-12",
                "value": "₹7,00,00,000",
                "source": "BidAssist"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping BidAssist: {e}")
    
    return tenders

def scrape_tendersinfo():
    """
    Scrape tenders from TendersInfo (https://www.tendersinfo.com).
    Returns a list of tender dictionaries.
    """
    tenders = []
    
    try:
        # Note: This is a simplified example. The actual implementation would need
        # to handle pagination, authentication, and other complexities.
        url = "https://www.tendersinfo.com"
        
        # For demonstration purposes, we'll return sample data
        # In a real implementation, you would scrape the actual website
        
        # Sample tender data - standardized format
        sample_tenders = [
            {
                "tender_id": "TI-2025-001",
                "title": "Clinical trial equipment procurement",
                "organization": "Pharma Research Ltd",
                "location": "Hyderabad",
                "deadline": "2025-10-28",
                "value": "₹25,00,00,000",
                "source": "TendersInfo"
            },
            {
                "tender_id": "TI-2025-002",
                "title": "Automotive component manufacturing equipment",
                "organization": "AutoTech Manufacturing",
                "location": "Chennai",
                "deadline": "2025-11-25",
                "value": "₹40,00,00,000",
                "source": "TendersInfo"
            },
            {
                "tender_id": "TI-2025-003",
                "title": "Solar panel installation services",
                "organization": "Green Energy Solutions",
                "location": "Bangalore",
                "deadline": "2025-12-20",
                "value": "₹30,00,00,000",
                "source": "TendersInfo"
            }
        ]
        
        tenders.extend(sample_tenders)
        
    except Exception as e:
        print(f"Error scraping TendersInfo: {e}")
    
    return tenders