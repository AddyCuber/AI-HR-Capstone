#!/usr/bin/env python3
"""
Test script for the explainable AI matcher
"""

from explainable_matcher import ExplainableAIMatcher, ResumeHighlighter

def test_explainable_matcher():
    """Test the explainable matcher with sample data"""
    
    # Sample resume text
    resume_text = """
    John Doe
    john.doe@email.com
    (555) 123-4567
    
    Skills: Python, JavaScript, React, Node.js, AWS, Docker
    
    Experience:
    - Software Engineer at TechCorp (2020-2023)
    - Junior Developer at StartupXYZ (2018-2020)
    
    Education:
    - Bachelor of Science in Computer Science from State University
    """
    
    # Sample job description
    job_description = """
    Senior Software Engineer
    
    We are looking for a Senior Software Engineer with:
    - 5+ years of experience in Python and JavaScript
    - Experience with React and Node.js
    - Knowledge of cloud platforms (AWS, Azure)
    - Experience with Docker and Kubernetes
    - Strong leadership skills
    - Experience with machine learning is a plus
    """
    
    print("🧪 Testing Explainable AI Matcher...")
    
    # Initialize matcher
    matcher = ExplainableAIMatcher()
    
    # Test the matching
    result = matcher.match_with_explanations(resume_text, job_description)
    
    if result:
        print(f"✅ Match Score: {result.match_score}%")
        print(f"📝 Summary: {result.summary}")
        print(f"🔍 Number of explanations: {len(result.explanations)}")
        
        # Display explanations
        print("\n📊 Phrase-Level Analysis:")
        for i, exp in enumerate(result.explanations, 1):
            print(f"{i}. Phrase: '{exp.phrase}'")
            print(f"   Weight: {exp.weight}")
            print(f"   Justification: {exp.justification}")
            print(f"   Category: {exp.category}")
            print(f"   Section: {exp.resume_section}")
            print()
        
        # Test highlighting
        print("🎨 Testing resume highlighting...")
        highlighted = matcher.highlight_resume_text(resume_text, result.explanations)
        print("Highlighted resume text generated successfully!")
        
    else:
        print("❌ Explainable matching failed")

if __name__ == "__main__":
    test_explainable_matcher() 