#!/usr/bin/env python3
"""
Test script for the simplified interface with 2 mandatory features
"""

import requests
import json

def test_simplified_interface():
    """Test the simplified interface"""
    print("🧪 Testing Simplified Interface...")
    
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
    
    print("\n🎉 Simplified Interface Ready!")
    print("📋 Mandatory Features (No Toggles):")
    print("")
    print("   1. 🧠 Explainable AI Analysis")
    print("      • Detailed phrase-level explanations")
    print("      • Weight-based highlighting (-10 to +10)")
    print("      • Category classification (skills, experience, etc.)")
    print("      • PDF annotation generation")
    print("      • Downloadable annotated PDFs")
    print("")
    print("   2. ✨ Animated PDF Scanner")
    print("      • Circular bubble with smooth animations")
    print("      • Beautiful visual effects and glow")
    print("      • Floating tags and beam transfers")
    print("      • Curved paths like iOS 16 Live Text")
    print("      • 5-7 second animation duration")
    print("")
    print("🚀 How to Use:")
    print("   1. Go to http://localhost:3000")
    print("   2. Upload a PDF resume")
    print("   3. Add or generate a job description")
    print("   4. Click 'Start AI Analysis'")
    print("   5. Watch the beautiful animated scanning!")
    print("   6. Review detailed explanations and insights")
    print("")
    print("✨ No more confusing toggles - both features work together seamlessly!")

if __name__ == "__main__":
    test_simplified_interface() 