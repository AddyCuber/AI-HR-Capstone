#!/usr/bin/env python3
"""
Test script for Explainable AI Analysis
"""

import requests
import json

def test_explainable_analysis():
    """Test the explainable analysis endpoint"""
    
    # Test data
    resume_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
        "experience": [
            {
                "role": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "description": "Led development of scalable web applications using React and Node.js. Improved system performance by 40% and reduced deployment time by 60%."
            },
            {
                "role": "Software Developer",
                "company": "Startup Inc",
                "duration": "2018-2020",
                "description": "Developed REST APIs and microservices using Python and Docker. Collaborated with cross-functional teams to deliver high-quality software."
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "year": "2018",
                "gpa": "3.8"
            }
        ],
        "projects": [
            "Built a real-time chat application using WebSocket and React",
            "Developed an e-commerce platform with payment integration",
            "Created a machine learning model for customer segmentation"
        ],
        "certifications": [
            "AWS Certified Developer",
            "Google Cloud Professional Developer"
        ],
        "achievements": [
            "Led a team of 5 developers to deliver project 2 weeks ahead of schedule",
            "Reduced database query time by 50% through optimization",
            "Mentored 3 junior developers and improved team productivity"
        ]
    }
    
    job_description = """
    Senior Full Stack Developer
    
    We are looking for a talented Senior Full Stack Developer to join our growing team. 
    The ideal candidate will have strong experience in modern web technologies and a passion for building scalable applications.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in JavaScript, React, and Node.js
    - Experience with cloud platforms (AWS, Azure, or GCP)
    - Knowledge of containerization (Docker, Kubernetes)
    - Experience with database design and optimization
    - Strong problem-solving skills and attention to detail
    - Experience with agile development methodologies
    - Excellent communication and teamwork skills
    
    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Mentor junior developers
    - Optimize application performance
    - Implement best practices and coding standards
    - Participate in code reviews and technical discussions
    
    Nice to have:
    - Experience with Python and Django
    - Knowledge of machine learning concepts
    - Experience with microservices architecture
    - Familiarity with CI/CD pipelines
    """
    
    # Test request
    request_data = {
        "resume_data": resume_data,
        "job_description": job_description,
        "analysis_type": "explainable"
    }
    
    try:
        # Make request to the API
        response = requests.post(
            "http://localhost:8001/match-resume",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Explainable Analysis Test Successful!")
            print(f"Match Score: {result.get('match_score', 0)}%")
            print(f"Summary: {result.get('summary', 'N/A')}")
            print(f"Number of explanations: {len(result.get('explanations', []))}")
            
            # Show some example explanations
            explanations = result.get('explanations', [])
            if explanations:
                print("\n📋 Sample Explanations:")
                for i, exp in enumerate(explanations[:3]):  # Show first 3
                    print(f"  {i+1}. '{exp.get('phrase', 'N/A')}'")
                    print(f"     Weight: {exp.get('weight', 0)}/10")
                    print(f"     Category: {exp.get('category', 'N/A')}")
                    print(f"     Justification: {exp.get('justification', 'N/A')}")
                    print()
            
            print(f"Strengths: {len(result.get('strengths', []))} items")
            print(f"Weaknesses: {len(result.get('weaknesses', []))} items")
            print(f"Suggestions: {len(result.get('suggestions', []))} items")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Explainable AI Analysis...")
    test_explainable_analysis() 