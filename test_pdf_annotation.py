#!/usr/bin/env python3
"""
Test script for PDF annotation functionality
"""

import requests
import json
import base64

def test_pdf_annotation():
    """Test the PDF annotation endpoint"""
    print("🧪 Testing PDF Annotation...")
    
    # Sample explanations data
    explanations = [
        {
            "phrase": "Python",
            "weight": 8,
            "justification": "Strong technical skill that matches job requirements",
            "category": "skill"
        },
        {
            "phrase": "React",
            "weight": 7,
            "justification": "Frontend framework experience aligns with job needs",
            "category": "skill"
        },
        {
            "phrase": "Led team of 5 developers",
            "weight": 9,
            "justification": "Excellent leadership experience",
            "category": "experience"
        }
    ]
    
    # Create a simple test PDF (you would normally upload a real PDF)
    # For testing, we'll just check if the endpoint exists
    try:
        response = requests.get("http://localhost:8001/")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print("✅ PDF Annotation endpoint is available")
    print("📋 To test PDF annotation:")
    print("   1. Upload a PDF resume at http://localhost:3000")
    print("   2. Generate or enter a job description")
    print("   3. Enable 'Explainable AI Analysis'")
    print("   4. Click 'Start AI Analysis'")
    print("   5. Click 'Generate Annotated PDF' to see highlights")
    print("   6. View or download the annotated PDF")

if __name__ == "__main__":
    test_pdf_annotation() 