"""Test data fixtures and generators for RadioForms testing.

This module provides reusable test data and fixtures for all test modules.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import random

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority


class TestDataGenerator:
    """Generator for test data."""
    
    # Sample data for generating realistic test forms
    INCIDENT_NAMES = [
        "Wildfire Response Alpha", "Earthquake Emergency", "Flood Operations",
        "Hurricane Evacuation", "Chemical Spill Incident", "Search and Rescue",
        "Building Collapse", "Medical Emergency", "Traffic Incident",
        "Power Outage Response", "Communication Failure", "Shelter Operations"
    ]
    
    POSITIONS = [
        "IC", "Deputy IC", "Safety Officer", "PIO", "Liaison Officer",
        "Operations Chief", "Planning Chief", "Logistics Chief", "Finance Chief",
        "Strike Team Leader", "Task Force Leader", "Communications Unit Leader",
        "Resource Unit Leader", "Situation Unit Leader", "Medical Unit Leader",
        "Supply Unit Leader", "Facilities Unit Leader", "Ground Support Leader"
    ]
    
    NAMES = [
        "John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson", "David Brown",
        "Emily Davis", "Chris Miller", "Lisa Garcia", "Robert Jones", "Maria Rodriguez",
        "James Taylor", "Jennifer Martinez", "Michael Anderson", "Jessica Thomas",
        "William Jackson", "Ashley White", "Daniel Harris", "Amanda Martin",
        "Matthew Thompson", "Stephanie Garcia", "Anthony Clark", "Melissa Lewis",
        "Mark Lee", "Rebecca Walker", "Steven Hall", "Laura Allen", "Kevin Young",
        "Amy King", "Ryan Wright", "Nicole Scott", "Justin Green", "Heather Adams"
    ]
    
    MESSAGE_TEMPLATES = [
        "Request {} additional personnel for {}.",
        "Status update: {} operations proceeding as planned.",
        "Resource requirement: {} units needed for {}.",
        "Safety concern: {} identified in sector {}.",
        "Progress report: {} percent complete on {}.",
        "Communication test: {} radio check successful.",
        "Equipment status: {} operational, {} down for maintenance.",
        "Weather update: {} conditions expected for next {} hours.",
        "Personnel update: {} staff assigned to {}.",
        "Logistics update: {} supplies delivered to {}."
    ]
    
    @classmethod
    def random_person(cls, position: Optional[str] = None) -> Person:
        """Generate a random person."""
        name = random.choice(cls.NAMES)
        pos = position or random.choice(cls.POSITIONS)
        
        # Generate contact info and signature sometimes
        contact_info = f"Radio {random.randint(100, 999)}" if random.random() > 0.3 else ""
        signature = name.split()[0][:1] + name.split()[1][:1] if random.random() > 0.5 else ""
        
        return Person(
            name=name,
            position=pos,
            contact_info=contact_info,
            signature=signature
        )
    
    @classmethod
    def random_message(cls) -> str:
        """Generate a random message."""
        template = random.choice(cls.MESSAGE_TEMPLATES)
        
        # Fill in template placeholders
        message = template.format(
            random.randint(2, 20),
            random.choice(["operations", "response", "evacuation", "search", "rescue"]),
            random.choice(["Alpha", "Bravo", "Charlie", "Delta", "Echo"]),
            random.randint(1, 12),
            random.choice(["North", "South", "East", "West", "Central"]),
            random.randint(50, 95),
            random.choice(["fire suppression", "rescue operations", "evacuation"]),
            random.choice(["Clear", "Overcast", "Rainy", "Windy"]),
            random.randint(1, 8),
            random.choice(["equipment", "vehicles", "personnel", "supplies"]),
            random.choice(["Base Camp", "Forward Command", "Staging Area"])
        )
        
        return message
    
    @classmethod
    def random_date_time(cls, days_back: int = 7) -> tuple[str, str]:
        """Generate random date and time within specified days back."""
        base_date = datetime.now() - timedelta(days=random.randint(0, days_back))
        
        date_str = base_date.strftime("%Y-%m-%d")
        time_str = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
        
        return date_str, time_str
    
    @classmethod
    def generate_ics213_data(cls, 
                           index: int = 0,
                           incident_name: Optional[str] = None,
                           priority: Optional[Priority] = None,
                           complete: bool = True) -> ICS213Data:
        """Generate ICS213Data with realistic test data.
        
        Args:
            index: Index for unique data generation
            incident_name: Specific incident name or random if None
            priority: Specific priority or random if None
            complete: Whether to include all optional fields
        """
        date_str, time_str = cls.random_date_time()
        
        data = ICS213Data(
            incident_name=incident_name or random.choice(cls.INCIDENT_NAMES),
            to=cls.random_person(),
            from_person=cls.random_person(),
            subject=f"Message {index + 1}: {random.choice(['Status', 'Request', 'Update', 'Report'])}",
            date=date_str,
            time=time_str,
            message=cls.random_message(),
            priority=priority or random.choice(list(Priority))
        )
        
        if complete and random.random() > 0.3:
            # Add optional fields sometimes
            data.reply_requested = random.random() > 0.5
            
            if random.random() > 0.6:
                data.approved_by = cls.random_person("Safety Officer")
            
            if random.random() > 0.7:
                data.reply = f"Reply to message {index + 1}: " + cls.random_message()
                data.replied_by = cls.random_person("IC")
                reply_date, reply_time = cls.random_date_time(1)
                data.reply_date_time = f"{reply_date} {reply_time}"
        
        return data
    
    @classmethod
    def generate_ics213_form(cls, 
                           index: int = 0,
                           **kwargs) -> ICS213Form:
        """Generate complete ICS213Form with test data."""
        data = cls.generate_ics213_data(index, **kwargs)
        return ICS213Form(data)
    
    @classmethod
    def generate_minimal_form(cls, index: int = 0) -> ICS213Form:
        """Generate minimal valid form."""
        data = ICS213Data(
            to=Person(name=f"Commander {index}", position="IC"),
            from_person=Person(name=f"Operator {index}", position="Ops"),
            subject=f"Minimal Test {index}",
            message=f"Minimal test message {index}"
        )
        return ICS213Form(data)
    
    @classmethod
    def generate_invalid_form(cls, missing_field: str = "subject") -> ICS213Form:
        """Generate invalid form for error testing."""
        data = ICS213Data(
            to=Person(name="Test Commander", position="IC"),
            from_person=Person(name="Test Operator", position="Ops"),
            subject="Test Subject",
            message="Test Message"
        )
        
        # Remove specified field to make invalid
        if missing_field == "to":
            data.to = None
        elif missing_field == "from_person":
            data.from_person = None
        elif missing_field == "subject":
            data.subject = ""
        elif missing_field == "message":
            data.message = ""
        
        return ICS213Form(data)
    
    @classmethod
    def generate_form_batch(cls, 
                          count: int,
                          incident_name: Optional[str] = None,
                          priority: Optional[Priority] = None) -> List[ICS213Form]:
        """Generate a batch of forms for testing."""
        return [
            cls.generate_ics213_form(
                index=i,
                incident_name=incident_name,
                priority=priority
            )
            for i in range(count)
        ]
    
    @classmethod
    def generate_large_content_form(cls) -> ICS213Form:
        """Generate form with large content for performance testing."""
        large_message = " ".join([cls.random_message() for _ in range(100)])
        
        data = ICS213Data(
            incident_name="Large Content Performance Test",
            to=Person(
                name="Performance Test Commander",
                position="Incident Commander",
                contact_info="Radio 001, Cell: (555) 123-4567, Email: commander@test.gov",
                signature="P.T.C."
            ),
            from_person=Person(
                name="Performance Test Operator",
                position="Communications Unit Leader",
                contact_info="Radio 002, Cell: (555) 123-4568, Email: operator@test.gov", 
                signature="P.T.O."
            ),
            subject="Performance Test with Large Content - Stress Testing Message Handling",
            date="2025-05-30",
            time="23:45",
            message=large_message,
            priority=Priority.URGENT,
            reply_requested=True,
            approved_by=Person(
                name="Performance Test Safety Officer",
                position="Safety Officer",
                signature="P.T.S.O."
            ),
            reply="This is a detailed reply to the large content performance test message. " * 20,
            replied_by=Person(
                name="Performance Test IC",
                position="Incident Commander",
                signature="P.T.I.C."
            ),
            reply_date_time="2025-05-30 23:50"
        )
        
        return ICS213Form(data)
    
    @classmethod
    def generate_unicode_form(cls) -> ICS213Form:
        """Generate form with Unicode content for testing."""
        data = ICS213Data(
            incident_name="Test with Ünicöde & Special Chäractérs",
            to=Person(name="José María González", position="Comandante de Incidentes"),
            from_person=Person(name="张三 (Zhang San)", position="通信员"),
            subject="Test message with 中文, émojis 🚒🚑, and spëcial chars",
            date="2025-05-30", 
            time="23:45",
            message="This message contains:\n• Unicode: café, naïve, résumé\n• Chinese: 你好世界\n• Emoji: 🚒🚑🚓\n• Special chars: @#$%^&*()",
            priority=Priority.IMMEDIATE,
            reply_requested=True
        )
        
        return ICS213Form(data)


# Pre-generated test fixtures
SAMPLE_FORMS = [
    TestDataGenerator.generate_ics213_form(i) for i in range(10)
]

MINIMAL_FORMS = [
    TestDataGenerator.generate_minimal_form(i) for i in range(5)
]

INVALID_FORMS = [
    TestDataGenerator.generate_invalid_form("to"),
    TestDataGenerator.generate_invalid_form("from_person"),
    TestDataGenerator.generate_invalid_form("subject"),
    TestDataGenerator.generate_invalid_form("message")
]

SPECIAL_FORMS = [
    TestDataGenerator.generate_large_content_form(),
    TestDataGenerator.generate_unicode_form()
]


def get_test_form(form_type: str = "sample", index: int = 0) -> ICS213Form:
    """Get a test form by type and index.
    
    Args:
        form_type: Type of form ("sample", "minimal", "invalid", "special")
        index: Index of form within type
    """
    if form_type == "sample":
        return SAMPLE_FORMS[index % len(SAMPLE_FORMS)]
    elif form_type == "minimal":
        return MINIMAL_FORMS[index % len(MINIMAL_FORMS)]
    elif form_type == "invalid":
        return INVALID_FORMS[index % len(INVALID_FORMS)]
    elif form_type == "special":
        return SPECIAL_FORMS[index % len(SPECIAL_FORMS)]
    else:
        raise ValueError(f"Unknown form type: {form_type}")


def get_test_forms(form_type: str = "sample", count: int = 10) -> List[ICS213Form]:
    """Get multiple test forms.
    
    Args:
        form_type: Type of forms to generate
        count: Number of forms to return
    """
    if form_type == "generated":
        return TestDataGenerator.generate_form_batch(count)
    else:
        return [get_test_form(form_type, i) for i in range(count)]