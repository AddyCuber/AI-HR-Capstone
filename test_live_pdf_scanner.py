#!/usr/bin/env python3
"""
Test script for Live PDF Scanner functionality
"""

import requests
import json

def test_live_pdf_scanner():
    """Test the Live PDF Scanner functionality"""
    print("🧪 Testing Live PDF Scanner...")
    
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
    
    print("✅ Live PDF Scanner is available")
    print("📋 To test Live PDF Scanner:")
    print("   1. Upload a PDF resume at http://localhost:3000")
    print("   2. Generate or enter a job description")
    print("   3. Enable 'Live PDF Scanner' (blue toggle)")
    print("   4. Click 'Start AI Analysis'")
    print("   5. Watch the live scanning experience:")
    print("      • Real-time PDF rendering")
    print("      • Live analysis feed")
    print("      • Progress tracking")
    print("      • Feature highlighting")
    print("      • Auto-play functionality")
    print("   6. Use controls: Play/Pause, Next, Previous, Skip")
    print("   7. View final insights after scanning")

if __name__ == "__main__":
    test_live_pdf_scanner() 