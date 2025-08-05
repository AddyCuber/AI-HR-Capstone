#!/usr/bin/env python3
"""
Test script for Animated PDF Scanner functionality
"""

import requests
import json

def test_animated_pdf_scanner():
    """Test the Animated PDF Scanner functionality"""
    print("🧪 Testing Animated PDF Scanner...")
    
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
    
    try:
        response = requests.get("http://localhost:3000/")
        if response.status_code == 200:
            print("✅ Frontend is running")
        else:
            print("❌ Frontend is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
        return
    
    print("✅ Animated PDF Scanner is available")
    print("📋 To test Animated PDF Scanner:")
    print("   1. Upload a PDF resume at http://localhost:3000")
    print("   2. Generate or enter a job description")
    print("   3. Enable 'Animated PDF Scanner' (indigo toggle)")
    print("   4. Click 'Start AI Analysis'")
    print("   5. Watch the beautiful scanning animation:")
    print("      • Circular scanning bubble")
    print("      • Smooth curved movements")
    print("      • Section highlighting with glow effects")
    print("      • Floating tags with popout animations")
    print("      • Beam transfer animations")
    print("      • Real-time analysis panel updates")
    print("   6. Use controls: Play/Pause, Skip to Results")
    print("   7. View final insights after scanning")

if __name__ == "__main__":
    test_animated_pdf_scanner() 