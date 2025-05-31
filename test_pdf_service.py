#!/usr/bin/env python3
"""
Test script for PDF generation service.

This script validates the PDF generation functionality for ICS forms,
creating sample PDFs to verify layout, formatting, and functionality.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, 'src')

try:
    # Import form models
    from forms.ics213 import ICS213Form, ICS213Data, Person, Priority
    from models.ics214 import ICS214Form, ICS214Data, ActivityEntry, ResourceAssignment, OperationalPeriod
    from services.pdf_service import PDFService, create_pdf_service, generate_form_pdf
    
    print("✅ All imports successful")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def create_sample_ics213() -> ICS213Form:
    """Create a sample ICS-213 form with test data."""
    
    # Create person objects
    recipient = Person(
        name="John Smith",
        position="Incident Commander",
        contact_info="Radio 101"
    )
    
    sender = Person(
        name="Jane Doe", 
        position="Operations Section Chief",
        contact_info="Radio 201"
    )
    
    approver = Person(
        name="Chief Johnson",
        position="Agency Administrator",
        signature="CJ"
    )
    
    # Create form data
    data = ICS213Data(
        incident_name="Mountain View Wildfire",
        to=recipient,
        from_person=sender,
        subject="Resource Request - Additional Fire Engines",
        date="2025-05-30",
        time="14:30",
        message="Requesting immediate deployment of 3 additional fire engines to Division A. "
                "Current fire behavior is extreme with rapid eastward spread. Structures at risk. "
                "Engines should report to Division A supervisor on arrival. ETA requested ASAP.",
        approved_by=approver,
        priority=Priority.URGENT,
        reply_requested=True
    )
    
    # Create form and add reply
    form = ICS213Form(data)
    
    # Add a reply
    replier = Person(name="John Smith", position="Incident Commander")
    form.add_reply(
        "Approved. Three engines (E5240, E5241, E5242) dispatched from Station 15. "
        "ETA Division A: 15 minutes. Contact Division A supervisor on Channel 8.",
        replier
    )
    
    return form


def create_sample_ics214() -> ICS214Form:
    """Create a sample ICS-214 form with test data."""
    
    # Create operational period
    op_period = OperationalPeriod(
        from_date="2025-05-30",
        from_time="08:00",
        to_date="2025-05-30", 
        to_time="20:00"
    )
    
    # Create resources
    resources = [
        ResourceAssignment(
            name="Engine 5240",
            ics_position="Single Resource",
            home_agency="CAL FIRE - Unit 5240"
        ),
        ResourceAssignment(
            name="Strike Team Alpha",
            ics_position="Strike Team",
            home_agency="CAL FIRE - Region 5"
        )
    ]
    
    # Create activities
    activities = [
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 8, 0),
            notable_activities="Arrived on scene, assumed Operations Section Chief role"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 8, 30),
            notable_activities="Briefed by previous Operations Chief, reviewed IAP"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 9, 0),
            notable_activities="Established operational divisions, deployed initial resources"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 10, 30),
            notable_activities="Fire spotted across containment line in Division B, ordered additional resources"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 12, 0),
            notable_activities="Lunch break rotation initiated, maintained 75% staffing"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 14, 30),
            notable_activities="Extreme fire behavior observed, ordered evacuation of Division A"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 16, 0),
            notable_activities="Additional air support requested and approved"
        ),
        ActivityEntry(
            datetime=datetime(2025, 5, 30, 18, 30),
            notable_activities="Containment achieved on east flank, resources reassigned"
        )
    ]
    
    # Create prepared by person
    prepared_by = Person(
        name="Jane Doe",
        position="Operations Section Chief"
    )
    
    # Create form data
    data = ICS214Data(
        incident_name="Mountain View Wildfire",
        operational_period=op_period,
        name="Jane Doe",
        ics_position="Operations Section Chief",
        home_agency="CAL FIRE - Unit 5200",
        resources_assigned=resources,
        activity_log=activities,
        prepared_by=prepared_by
    )
    
    return ICS214Form(data)


def test_pdf_generation():
    """Test PDF generation for both form types."""
    
    print("\n🧪 Testing PDF Generation Service")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("test_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Test 1: Create PDF service
        print("\n1. Creating PDF service...")
        pdf_service = create_pdf_service(output_dir)
        print(f"   ✅ PDF service created with output dir: {output_dir}")
        
        # Test 2: Generate ICS-213 PDF
        print("\n2. Generating ICS-213 PDF...")
        ics213_form = create_sample_ics213()
        
        # Validate form first
        if not ics213_form.validate():
            print(f"   ❌ ICS-213 form validation failed: {ics213_form.get_validation_errors()}")
            return False
        
        ics213_path = pdf_service.generate_pdf(ics213_form, output_dir / "sample_ics213.pdf")
        print(f"   ✅ ICS-213 PDF generated: {ics213_path}")
        
        # Test 3: Generate ICS-214 PDF  
        print("\n3. Generating ICS-214 PDF...")
        ics214_form = create_sample_ics214()
        
        # Validate form first
        validation_result = ics214_form.validate_detailed()
        if not validation_result.is_valid:
            print(f"   ❌ ICS-214 form validation failed: {validation_result.errors}")
            return False
        
        ics214_path = pdf_service.generate_pdf(ics214_form, output_dir / "sample_ics214.pdf")
        print(f"   ✅ ICS-214 PDF generated: {ics214_path}")
        
        # Test 4: Test convenience function
        print("\n4. Testing convenience function...")
        convenience_path = output_dir / "convenience_test.pdf"
        result_path = generate_form_pdf(ics213_form, convenience_path)
        print(f"   ✅ Convenience function PDF generated: {result_path}")
        
        # Test 5: Verify file sizes
        print("\n5. Verifying generated files...")
        for pdf_path in [ics213_path, ics214_path, result_path]:
            if pdf_path.exists():
                size = pdf_path.stat().st_size
                print(f"   ✅ {pdf_path.name}: {size:,} bytes")
            else:
                print(f"   ❌ {pdf_path.name}: File not found")
                return False
        
        print("\n🎉 All PDF generation tests passed!")
        print(f"\n📂 Generated PDFs are available in: {output_dir.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ PDF generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test execution."""
    print("PDF Service Test Suite")
    print("=" * 50)
    
    # Run tests
    success = test_pdf_generation()
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()