#!/usr/bin/env python3
"""
Simple test for PDF generation without complex imports.

This tests ReportLab availability and basic PDF creation.
"""

import sys
import os
from pathlib import Path

def test_reportlab_import():
    """Test if ReportLab is available."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        print("✅ ReportLab imports successful")
        return True
    except ImportError as e:
        print(f"❌ ReportLab import failed: {e}")
        print("   Install ReportLab with: pip install reportlab")
        return False

def test_basic_pdf_generation():
    """Test basic PDF generation functionality."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Create output directory
        output_dir = Path("test_pdfs")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple PDF
        output_path = output_dir / "test_basic.pdf"
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create content
        story = []
        story.append(Paragraph("Test PDF Generation", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("This is a test of basic PDF generation using ReportLab.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Check if file was created
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"✅ Basic PDF generated: {output_path} ({size:,} bytes)")
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Basic PDF generation failed: {e}")
        return False

def main():
    """Main test execution."""
    print("PDF Generation Test - Basic")
    print("=" * 40)
    
    # Test 1: ReportLab availability
    print("\n1. Testing ReportLab import...")
    if not test_reportlab_import():
        print("\n❌ ReportLab not available. Cannot proceed with PDF tests.")
        return False
    
    # Test 2: Basic PDF generation
    print("\n2. Testing basic PDF generation...")
    if not test_basic_pdf_generation():
        print("\n❌ Basic PDF generation failed.")
        return False
    
    print("\n✅ All basic PDF tests passed!")
    print("\nNext step: Install ReportLab if not already installed, then test form PDF generation.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)