"""
Tests for database operations.
"""
import pytest
from db.connection import get_db
from db.models import Tender
from datetime import datetime

def test_db_connection():
    """Test database connection."""
    db = get_db()
    assert db is not None

def test_tender_model():
    """Test Tender model creation and conversion."""
    tender = Tender(
        tender_id="TEST-001",
        organization="Test Organization",
        category="Test Category",
        location="Test Location",
        value=100000.0,
        deadline=datetime(2025, 12, 31),
        description="Test tender description",
        link="http://test.com"
    )
    
    # Test to_dict conversion
    tender_dict = tender.to_dict()
    assert isinstance(tender_dict, dict)
    assert tender_dict["tender_id"] == "TEST-001"
    assert tender_dict["organization"] == "Test Organization"
    assert tender_dict["value"] == 100000.0
    
    # Test from_dict conversion
    new_tender = Tender.from_dict(tender_dict)
    assert new_tender.tender_id == tender.tender_id
    assert new_tender.organization == tender.organization
    assert new_tender.value == tender.value

if __name__ == "__main__":
    pytest.main([__file__])