# Backend Files for GitHub Upload

## Core Backend Files

### Main Files
- `run_backend.py` - Script to run the backend server
- `run_server.py` - Original server run script
- `backend_requirements.txt` - Backend dependencies
- `requirements.txt` - Full project dependencies
- `BACKEND_README.md` - Backend-specific documentation
- `README.md` - Full project documentation
- `.gitignore` - Git ignore file
- `setup_backend.py` - Backend setup script
- `test_backend.py` - Backend testing script

### API Module (`api/`)
- `__init__.py`
- `server.py` - FastAPI server implementation
- `filter.py` - Data filtering and ranking functionality

### Database Module (`db/`)
- `__init__.py`
- `connection.py` - Database connection handling
- `models.py` - Data models

### Agents Module (`agents/`)
- `__init__.py`
- `etenders.py` - eTenders portal scraper
- `gem.py` - GeM portal scraper

### NLP Module (`nlp/`)
- `__init__.py`
- `extract.py` - Data extraction using NLP

### Big Data Module (`big_data/`)
- `__init__.py`
- `data_processor.py` - Large dataset processing

### Export Module (`export/`)
- `__init__.py`
- `data_exporter.py` - Data export functionality

### Tests Module (`tests/`)
- `__init__.py`
- `test_db.py` - Database tests
- `test_filter.py` - Filter tests
- `test_scraper.py` - Scraper tests

## Files to Exclude (handled by .gitignore)
- `__pycache__/` directories
- `.pytest_cache/` directory
- `exports/` directory
- `.env` files
- IDE-specific files
- Generated files like `*.json`, `*.xlsx`