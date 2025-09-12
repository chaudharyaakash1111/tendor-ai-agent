# Tender Aggregator

A Python application that scrapes government tender portals, processes the data with NLP, and provides a REST API for querying tenders.

## Features
- Scrapes eTenders and GeM portals
- Extracts structured data using NLP
- Stores data in MongoDB
- Provides REST API for querying tenders
- Export data to JSON and Excel formats
- Streamlit frontend for easy access
- Big data processing for large datasets

## Tech Stack
- Python
- Web Scraping: requests, BeautifulSoup4, Selenium
- NLP: spaCy
- Database: MongoDB
- Backend API: FastAPI
- Frontend: Streamlit
- Data Export: pandas, openpyxl

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Install spaCy model: `python -m spacy download en_core_web_sm`
3. Run the application: `python main.py`

## API Endpoints
- GET /tenders - Get all tenders
- GET /tenders/search - Search tenders with filters
- GET /tenders/{tender_id} - Get a specific tender
- GET /export - Export all tenders (format=json or format=excel)
- GET /export/big - Export large datasets efficiently (format=json or format=excel)
- GET /stats - Get dataset statistics

## Data Export
To export all tenders to JSON and Excel formats:
- Run the export script: `python run_export.py`
- Or use the API endpoint: `GET /export?format=json` or `GET /export?format=excel`
- Or use the Streamlit UI: Navigate to "Export Data" page

## Big Data Processing
For large datasets with thousands of records:
- Run the big data processing script: `python process_big_data.py`
- Or use the API endpoint: `GET /export/big?format=json` or `GET /export/big?format=excel`
- Or use the Streamlit UI: Navigate to "Big Data Processing" page

## Streamlit Frontend
To run the Streamlit frontend:
1. Make sure the FastAPI server is running: `python run_server.py`
2. Run the Streamlit app: `streamlit run ui/app.py`