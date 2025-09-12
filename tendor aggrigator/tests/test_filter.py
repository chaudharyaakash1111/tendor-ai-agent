"""
Tests for filter and ranking functionality.
"""
import pytest
from api.filter import filter_tenders, rank_tenders
from datetime import datetime, timedelta

@pytest.fixture
def sample_tenders():
    """Sample tenders for testing."""
    return [
        {
            "tender_id": "T1",
            "organization": "Ministry of Electronics",
            "category": "IT Services",
            "location": "Delhi",
            "value": 100000.0,
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "description": "Software development services",
            "link": "http://test1.com"
        },
        {
            "tender_id": "T2",
            "organization": "Department of Roads",
            "category": "Construction",
            "location": "Mumbai",
            "value": 500000.0,
            "deadline": (datetime.now() + timedelta(days=15)).isoformat(),
            "description": "Road construction project",
            "link": "http://test2.com"
        },
        {
            "tender_id": "T3",
            "organization": "Health Ministry",
            "category": "Medical Equipment",
            "location": "Delhi",
            "value": 250000.0,
            "deadline": (datetime.now() + timedelta(days=45)).isoformat(),
            "description": "Medical devices procurement",
            "link": "http://test3.com"
        }
    ]

def test_filter_by_organization(sample_tenders):
    """Test filtering by organization."""
    filters = {"organization": "Ministry"}
    filtered = filter_tenders(sample_tenders, filters)
    assert len(filtered) == 2
    for tender in filtered:
        assert "Ministry" in tender["organization"]

def test_filter_by_category(sample_tenders):
    """Test filtering by category."""
    filters = {"category": "Construction"}
    filtered = filter_tenders(sample_tenders, filters)
    assert len(filtered) == 1
    assert filtered[0]["category"] == "Construction"

def test_filter_by_location(sample_tenders):
    """Test filtering by location."""
    filters = {"location": "Delhi"}
    filtered = filter_tenders(sample_tenders, filters)
    assert len(filtered) == 2
    for tender in filtered:
        assert "Delhi" in tender["location"]

def test_filter_by_value_range(sample_tenders):
    """Test filtering by value range."""
    filters = {"min_value": 150000.0, "max_value": 300000.0}
    filtered = filter_tenders(sample_tenders, filters)
    assert len(filtered) == 1
    assert filtered[0]["tender_id"] == "T3"

def test_ranking_by_deadline(sample_tenders):
    """Test ranking by deadline."""
    ranked = rank_tenders(sample_tenders)
    # T2 should come first as it has the earliest deadline
    assert ranked[0]["tender_id"] == "T2"

def test_ranking_with_query(sample_tenders):
    """Test ranking with keyword query."""
    ranked = rank_tenders(sample_tenders, "medical")
    # T3 should come first as it matches the query
    assert ranked[0]["tender_id"] == "T3"

if __name__ == "__main__":
    pytest.main([__file__])