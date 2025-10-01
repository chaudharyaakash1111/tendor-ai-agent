"""
Database models for Tender Aggregator.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Tender:
    tender_id: str
    organization: str
    category: str
    location: str
    value: float
    deadline: datetime
    description: str
    link: str
    
    def to_dict(self):
        return {
            "tender_id": self.tender_id,
            "organization": self.organization,
            "category": self.category,
            "location": self.location,
            "value": self.value,
            "deadline": self.deadline.isoformat() if isinstance(self.deadline, datetime) else self.deadline,
            "description": self.description,
            "link": self.link
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            tender_id=data["tender_id"],
            organization=data["organization"],
            category=data["category"],
            location=data["location"],
            value=data["value"],
            deadline=data["deadline"],
            description=data["description"],
            link=data["link"]
        )