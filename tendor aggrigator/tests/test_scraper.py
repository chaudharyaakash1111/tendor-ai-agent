"""
Tests for scraping agents.
"""
import pytest
from agents.etenders import scrape_etenders
from agents.gem import scrape_gem

def test_etenders_scraper():
    """Test eTenders scraper returns data."""
    tenders = scrape_etenders()
    assert isinstance(tenders, list)
    assert len(tenders) > 0
    # Check that each tender has required fields
    for tender in tenders:
        assert "tender_id" in tender
        assert "organization" in tender
        assert "category" in tender
        assert "location" in tender
        assert "value" in tender
        assert "deadline" in tender
        assert "description" in tender
        assert "link" in tender

def test_gem_scraper():
    """Test GeM scraper returns data."""
    tenders = scrape_gem()
    assert isinstance(tenders, list)
    assert len(tenders) > 0
    # Check that each tender has required fields
    for tender in tenders:
        assert "tender_id" in tender
        assert "organization" in tender
        assert "category" in tender
        assert "location" in tender
        assert "value" in tender
        assert "deadline" in tender
        assert "description" in tender
        assert "link" in tender

if __name__ == "__main__":
    pytest.main([__file__])