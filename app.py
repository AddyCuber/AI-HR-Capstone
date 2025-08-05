import streamlit as st
import os
import json
import PyPDF2
import pdfplumber
import requests
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import tempfile
import io
import re
from datetime import datetime
import base64
from docx import Document
import fitz  # PyMuPDF for better PDF handling
from few_shot_examples import FEW_SHOT_EXAMPLES, PARSING_EXAMPLES, MATCHING_PROMPTS
from explainable_matcher import ExplainableAIMatcher, ResumeHighlighter

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Resume AI Matcher Pro",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'match_results' not in st.session_state:
    st.session_state.match_results = None
if 'enhanced_resume' not in st.session_state:
    st.session_state.enhanced_resume = None
if 'explainable_results' not in st.session_state:
    st.session_state.explainable_results = None
if 'uploaded_file_bytes' not in st.session_state:
    st.session_state.uploaded_file_bytes = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

class AdvancedResumeParser:
    """Advanced AI-powered resume parser with few-shot learning"""
    
    # Use comprehensive few-shot examples
    FEW_SHOT_EXAMPLES = PARSING_EXAMPLES
    
    @staticmethod
    def extract_text_from_file(uploaded_file) -> str:
        """Extract text from PDF, DOCX, or other file formats"""
        try:
            file_type = uploaded_file.type
            
            if file_type == "application/pdf":
                return AdvancedResumeParser._extract_from_pdf(uploaded_file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return AdvancedResumeParser._extract_from_docx(uploaded_file)
            else:
                return uploaded_file.read().decode('utf-8')
        except Exception as e:
            st.error(f"Error extracting text: {e}")
            return ""
    
    @staticmethod
    def _extract_from_pdf(uploaded_file) -> str:
        """Extract text from PDF using multiple methods"""
        try:
            # Try PyMuPDF first (best for complex layouts)
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
            return text
        except Exception as e:
            st.warning(f"PyMuPDF failed, trying pdfplumber: {e}")
            try:
                # Reset file pointer
                uploaded_file.seek(0)
                with pdfplumber.open(uploaded_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                    return text
            except Exception as e2:
                st.warning(f"pdfplumber failed, trying PyPDF2: {e2}")
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
                except Exception as e3:
                    st.error(f"All PDF extraction methods failed: {e3}")
                    return ""
    
    @staticmethod
    def _extract_from_docx(uploaded_file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(uploaded_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting from DOCX: {e}")
            return ""
    
    @staticmethod
    def parse_resume_with_ai(text: str) -> Dict[str, Any]:
        """Parse resume using AI with few-shot learning"""
        # This would use actual AI in production
        # For now, using enhanced rule-based parsing with few-shot examples
        
        parsed_data = {
            "name": "",
            "email": "",
            "phone": "",
            "education": [],
            "experience": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "achievements": []
        }
        
        # Extract email using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            parsed_data["email"] = emails[0]
        
        # Extract phone using regex
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            parsed_data["phone"] = phones[0]
        
        # Enhanced skill extraction with few-shot learning
        skill_keywords = [
            
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'machine learning', 'ai', 'data science',
            'html', 'css', 'git', 'agile', 'scrum', 'project management',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
            'spring boot', 'django', 'flask', 'express.js', 'vue.js', 'angular',
            'postgresql', 'mysql', 'redis', 'elasticsearch', 'jenkins', 'ci/cd',
            'microservices', 'rest api', 'graphql', 'websockets', 'oauth', 'jwt',
            # AI/ML specific skills
            'transformers', 'huggingface', 'langchain', 'whisper', 'whisperx',
            'faiss', 'modal', 'llm', 'prompt engineering', 'fastapi', 'streamlit',
            'spacy', 'openai', 'gemini', 'claude', 'bert', 'gpt', 'llama',
            'vector store', 'embeddings', 'nlp', 'natural language processing',
            'speech recognition', 'speaker detection', 'diarization', 's3'
            
        ]
        
        found_skills = []
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                found_skills.append(skill.title())
        
        parsed_data["skills"] = found_skills
        
        # Extract name using few-shot learning approach
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not '@' in line and not line.isdigit():
                # Check if it looks like a name (has proper case, no special chars)
                if re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*$', line):
                    parsed_data["name"] = line
                    break
        
        # Extract experience using pattern matching with deduplication
        experience_patterns = [
            r'(\w+\s+\w+)\s+at\s+([^,\n]+)\s*\(?(\d{4}-\d{4}|\d{4}-\s*present|\d{4})\)?',
            r'([^,\n]+)\s*-\s*(\w+\s+\w+)\s*\(?(\d{4}-\d{4}|\d{4}-\s*present|\d{4})\)?'
        ]
        
        seen_experiences = set()  # Track unique experiences
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    role = match[0].strip()
                    company = match[1].strip()
                    duration = match[2].strip()
                    
                    # Create unique key for experience
                    experience_key = f"{role}@{company}@{duration}"
                    
                    # Only add if we haven't seen this experience before
                    if experience_key not in seen_experiences:
                        seen_experiences.add(experience_key)
                        parsed_data["experience"].append({
                            "role": role,
                            "company": company,
                            "duration": duration,
                            "description": ""
                        })
        
        # Extract education with deduplication
        education_patterns = [
            r'(Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.E|M\.E|B\.Sc|M\.Sc)\s+[^,\n]*',
            r'([A-Z][a-z]+)\s+University\s*[^,\n]*',
            r'([A-Z][a-z]+)\s+College\s*[^,\n]*'
        ]
        
        seen_degrees = set()  # Track unique degrees
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                degree = match.strip()
                # Filter out common false positives
                if (degree and 
                    degree not in seen_degrees and 
                    degree.lower() not in ['board', 'school', 'high', 'secondary', 'primary', 'middle'] and
                    len(degree) > 2):  # Avoid very short matches
                    seen_degrees.add(degree)
                    parsed_data["education"].append({
                        "degree": degree,
                        "institution": "",
                        "year": "",
                        "gpa": ""
                    })
        
        return parsed_data

class AdvancedAIMatcher:
    """Advanced AI matcher with few-shot learning and enhanced features"""
    
    def __init__(self):
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.provider = os.getenv('AI_MODEL_PROVIDER', 'mistral')
    
    def generate_job_description(self, role: str, keywords: str, industry: str = "") -> str:
        """Generate comprehensive job description using AI"""
        prompt = f"""
        Generate a detailed job description for a {role} position.
        
        Requirements:
        - Industry: {industry if industry else 'Technology'}
        - Key skills: {keywords}
        
        Include:
        1. Job title and overview
        2. Key responsibilities (5-7 bullet points)
        3. Required qualifications
        4. Preferred skills
        5. Experience requirements
        6. Benefits and company culture
        
        Make it professional, detailed, and attractive to candidates.
        """
        
        try:
            if self.provider == 'mistral' and self.mistral_api_key:
                return self._call_mistral(prompt)
            elif self.provider == 'openai' and self.openai_api_key:
                return self._call_openai(prompt)
            else:
                return self._generate_fallback_jd(role, keywords, industry)
        except Exception as e:
            st.error(f"Error generating job description: {e}")
            return self._generate_fallback_jd(role, keywords, industry)
    
    def _call_mistral(self, prompt: str) -> str:
        """Call Mistral AI API"""
        try:
            from mistralai.client import MistralClient
            from mistralai.models.chat_completion import ChatMessage
            
            client = MistralClient(api_key=self.mistral_api_key)
            messages = [ChatMessage(role="user", content=prompt)]
            
            chat_response = client.chat(
                model="mistral-large-latest",
                messages=messages
            )
            
            return chat_response.choices[0].message.content
        except Exception as e:
            st.error(f"Mistral API error: {e}")
            return ""
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            return ""
    
    def _generate_fallback_jd(self, role: str, keywords: str, industry: str) -> str:
        """Generate a comprehensive job description without AI"""
        return f"""
        **{role.title()}**
        
        **Job Overview:**
        We are seeking a talented {role} to join our dynamic team in the {industry if industry else 'technology'} industry. This role offers exciting opportunities to work on cutting-edge projects and contribute to our company's success.
        
        **Key Responsibilities:**
        - Develop and maintain high-quality applications and systems
        - Collaborate with cross-functional teams to deliver innovative solutions
        - Write clean, maintainable, and well-documented code
        - Participate in code reviews and technical discussions
        - Stay updated with industry trends and best practices
        - Mentor junior developers and share knowledge
        - Contribute to architectural decisions and system design
        
        **Required Qualifications:**
        - Bachelor's degree in Computer Science, Engineering, or related field
        - Strong experience with: {keywords}
        - Excellent problem-solving and analytical skills
        - Strong communication and collaboration abilities
        - Experience with agile development methodologies
        
        **Preferred Skills:**
        - Experience with cloud platforms (AWS, Azure, GCP)
        - Knowledge of containerization and microservices
        - Familiarity with CI/CD pipelines
        - Experience with database design and optimization
        - Understanding of security best practices
        
        **Benefits:**
        - Competitive salary and benefits package
        - Flexible work arrangements
        - Professional development opportunities
        - Collaborative and inclusive work environment
        - Health and wellness programs
        """
    
    def match_resume_to_job(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Advanced matching with detailed analysis using few-shot learning"""
        
        # Get relevant few-shot examples based on job role
        role_keywords = job_description.lower()
        relevant_example = None
        
        if any(keyword in role_keywords for keyword in ['full stack', 'frontend', 'backend', 'web developer']):
            relevant_example = FEW_SHOT_EXAMPLES['full_stack_developer']
        elif any(keyword in role_keywords for keyword in ['ai/ml engineer', 'nlp engineer', 'machine learning engineer', 'ai engineer']):
            relevant_example = FEW_SHOT_EXAMPLES['ai_ml_engineer_nlp']
        elif any(keyword in role_keywords for keyword in ['data scientist', 'machine learning', 'analytics']):
            relevant_example = FEW_SHOT_EXAMPLES['data_scientist']
        elif any(keyword in role_keywords for keyword in ['devops', 'infrastructure', 'ci/cd']):
            relevant_example = FEW_SHOT_EXAMPLES['devops_engineer']
        
        # Create few-shot examples string
        few_shot_text = ""
        if relevant_example:
            few_shot_text = f"""
            Example Analysis:
            Job: {relevant_example['job_description']['role']} at {relevant_example['job_description']['company']}
            Requirements: {', '.join(relevant_example['job_description']['requirements'])}
            
            Candidate: {relevant_example['resume_data']['name']}
            Skills: {', '.join(relevant_example['resume_data']['skills'])}
            Experience: {len(relevant_example['resume_data']['experience'])} roles
            
            Expected Score: {relevant_example['expected_output']['match_score']}%
            Reasoning: {relevant_example['expected_output']['reasoning']['skills_match']}
            """
        
        prompt = f"""
        Analyze the following resume against the job description using these examples as reference:
        
        {few_shot_text}
        
        **Resume Data:**
        {json.dumps(resume_data, indent=2)}
        
        **Job Description:**
        {job_description}
        
        Provide a comprehensive analysis in JSON format:
        {{
            "match_score": 85,
            "reasoning": {{
                "skills_match": "Detailed analysis of skill overlap",
                "experience_alignment": "How well experience matches requirements", 
                "project_relevance": "Relevance of projects to job responsibilities",
                "bonus_factors": "Additional positive factors"
            }},
            "strengths": ["List of candidate strengths"],
            "missing": ["List of missing requirements"],
            "resume_enhancer": [
                {{
                    "current_line": "Current resume bullet point",
                    "suggestion": "Enhanced version with metrics and impact"
                }}
            ],
            "skill_gap_suggestions": ["Specific suggestions for improvement"],
            "learning_resources": [
                {{"topic": "Topic name", "link": "Resource URL"}}
            ]
        }}
        """
        
        try:
            if self.provider == 'mistral' and self.mistral_api_key:
                response = self._call_mistral(prompt)
            elif self.provider == 'openai' and self.openai_api_key:
                response = self._call_openai(prompt)
            else:
                st.info("ℹ️ Using fallback matching (no AI API configured)")
                return self._generate_fallback_match(resume_data, job_description)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                st.warning("⚠️ AI response parsing failed, using fallback matching")
                return self._generate_fallback_match(resume_data, job_description)
                
        except Exception as e:
            st.error(f"❌ Error in AI matching: {e}")
            st.info("ℹ️ Falling back to rule-based matching")
            return self._generate_fallback_match(resume_data, job_description)
    
    def _generate_fallback_match(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Generate comprehensive match results without AI using few-shot learning"""
        
        # Use few-shot examples for better fallback matching
        role_keywords = job_description.lower()
        relevant_example = None
        
        if any(keyword in role_keywords for keyword in ['full stack', 'frontend', 'backend', 'web developer']):
            relevant_example = FEW_SHOT_EXAMPLES['full_stack_developer']
        elif any(keyword in role_keywords for keyword in ['ai/ml engineer', 'nlp engineer', 'machine learning engineer', 'ai engineer']):
            relevant_example = FEW_SHOT_EXAMPLES['ai_ml_engineer_nlp']
        elif any(keyword in role_keywords for keyword in ['data scientist', 'machine learning', 'analytics']):
            relevant_example = FEW_SHOT_EXAMPLES['data_scientist']
        elif any(keyword in role_keywords for keyword in ['devops', 'infrastructure', 'ci/cd']):
            relevant_example = FEW_SHOT_EXAMPLES['devops_engineer']
        
        # Enhanced skill extraction from job description
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        jd_skills = set()
        
        # Comprehensive skill keywords based on few-shot examples
        common_skills = [
            'python', 'javascript', 'java', 'react', 'sql', 'aws', 'docker', 
            'machine learning', 'node.js', 'mongodb', 'kubernetes', 'git',
            'html', 'css', 'agile', 'scrum', 'project management',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
            'spring boot', 'django', 'flask', 'express.js', 'vue.js', 'angular',
            'postgresql', 'mysql', 'redis', 'elasticsearch', 'jenkins', 'ci/cd',
            'microservices', 'rest api', 'graphql', 'websockets', 'oauth', 'jwt',
            # AI/ML specific skills
            'transformers', 'huggingface', 'langchain', 'whisper', 'whisperx',
            'faiss', 'modal', 'llm', 'prompt engineering', 'fastapi', 'streamlit',
            'spacy', 'openai', 'gemini', 'claude', 'bert', 'gpt', 'llama',
            'vector store', 'embeddings', 'nlp', 'natural language processing',
            'speech recognition', 'speaker detection', 'diarization', 's3'
        ]
        
        for skill in common_skills:
            if skill in job_description.lower():
                jd_skills.add(skill)
        
        if jd_skills:
            skill_overlap = len(resume_skills.intersection(jd_skills))
            skills_score = min(100, (skill_overlap / len(jd_skills)) * 100)
        else:
            skills_score = 50
        
        # Calculate experience score based on few-shot examples
        experience_score = 70 if resume_data.get('experience') else 30
        if relevant_example:
            # Adjust based on example experience patterns
            example_exp_count = len(relevant_example['resume_data']['experience'])
            candidate_exp_count = len(resume_data.get('experience', []))
            if candidate_exp_count >= example_exp_count:
                experience_score = min(100, experience_score + 20)
        
        # Calculate education score
        education_score = 80 if resume_data.get('education') else 40
        
        # Ensure scores are properly calculated and not 0
        skills_score = max(10, skills_score)  # Minimum 10% if any skills exist
        experience_score = max(20, experience_score)  # Minimum 20% if experience exists
        education_score = max(30, education_score)  # Minimum 30% if education exists
        
        # Calculate overall score with weights from few-shot examples
        overall_score = (skills_score * 0.4 + experience_score * 0.4 + education_score * 0.2)
        
        # Generate enhanced suggestions based on few-shot examples
        strengths = ["Technical skills present", "Relevant background"]
        missing = ["Add more specific experience", "Include certifications"]
        recommendations = ["Highlight relevant projects", "Add more technical skills"]
        
        if relevant_example:
            # Use example-based suggestions
            strengths = relevant_example['expected_output']['strengths'][:2]  # Take first 2
            missing = relevant_example['expected_output']['missing'][:2]
            recommendations = relevant_example['expected_output']['skill_gap_suggestions'][:2]
        
        return {
            "match_score": int(overall_score),
            "reasoning": {
                "skills_match": f"Skill overlap analysis: {len(resume_skills.intersection(jd_skills))} matched, {len(jd_skills - resume_skills)} missing",
                "experience_alignment": f"Experience relevance: {experience_score}% based on role requirements",
                "project_relevance": "Project analysis based on job responsibilities",
                "bonus_factors": "Additional positive factors identified"
            },
            "strengths": strengths,
            "missing": missing,
            "resume_enhancer": [
                {
                    "current_line": "Current experience description",
                    "suggestion": "Enhanced version with metrics and impact"
                }
            ],
            "skill_gap_suggestions": recommendations,
            "learning_resources": [
                {"topic": "Skill Development", "link": "https://example.com/learning"},
                {"topic": "Best Practices", "link": "https://example.com/practices"}
            ]
        }
    
    def enhance_resume(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Generate resume enhancement suggestions"""
        prompt = f"""
        Analyze the resume and job description to provide specific enhancement suggestions.
        
        **Resume Data:**
        {json.dumps(resume_data, indent=2)}
        
        **Job Description:**
        {job_description}
        
        Provide enhancement suggestions in JSON format:
        {{
            "enhanced_bullet_points": [
                "Led development of scalable web application using React and Node.js, resulting in 40% performance improvement",
                "Implemented CI/CD pipeline reducing deployment time by 60%"
            ],
            "power_verbs": ["Spearheaded", "Architected", "Optimized", "Streamlined"],
            "quantified_achievements": ["Increased efficiency by 30%", "Reduced costs by 25%"],
            "skill_improvements": ["Add AWS certification", "Learn React framework"],
            "formatting_suggestions": ["Use action verbs", "Quantify achievements", "Highlight relevant projects"]
        }}
        """
        
        try:
            if self.provider == 'mistral' and self.mistral_api_key:
                response = self._call_mistral(prompt)
            elif self.provider == 'openai' and self.openai_api_key:
                response = self._call_openai(prompt)
            else:
                return self._generate_fallback_enhancement(resume_data, job_description)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return self._generate_fallback_enhancement(resume_data, job_description)
                
        except Exception as e:
            st.error(f"Error in resume enhancement: {e}")
            return self._generate_fallback_enhancement(resume_data, job_description)
    
    def _generate_fallback_enhancement(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Generate enhancement suggestions without AI"""
        return {
            "enhanced_bullet_points": [
                "Developed and maintained scalable applications using modern technologies",
                "Collaborated with cross-functional teams to deliver high-quality solutions",
                "Implemented best practices and coding standards"
            ],
            "power_verbs": ["Developed", "Implemented", "Collaborated", "Optimized"],
            "quantified_achievements": ["Improved performance by 25%", "Reduced bugs by 40%"],
            "skill_improvements": ["Add cloud computing experience", "Learn modern frameworks"],
            "formatting_suggestions": ["Use action verbs", "Quantify achievements", "Highlight relevant projects"]
        }

class PDFGenerator:
    """Generate PDF reports"""
    
    @staticmethod
    def generate_match_report(resume_data: Dict, job_description: str, match_results: Dict) -> str:
        """Generate a comprehensive PDF report"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("Resume Match Analysis Report", title_style))
            story.append(Spacer(1, 20))
            
            # Overall Score
            story.append(Paragraph(f"Overall Match Score: {match_results['match_score']}%", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Skills Analysis
            if 'skills_match' in match_results and isinstance(match_results['skills_match'], dict):
                story.append(Paragraph("Skills Analysis", styles['Heading2']))
                skills_data = match_results['skills_match']
                story.append(Paragraph(f"Skills Match Score: {skills_data.get('skills_score', 0)}%", styles['Normal']))
                
                if skills_data.get('matched_skills'):
                    story.append(Paragraph("Matched Skills:", styles['Normal']))
                    for skill in skills_data['matched_skills']:
                        story.append(Paragraph(f"• {skill}", styles['Normal']))
                
                if skills_data.get('missing_skills'):
                    story.append(Paragraph("Missing Skills:", styles['Normal']))
                    for skill in skills_data['missing_skills']:
                        story.append(Paragraph(f"• {skill}", styles['Normal']))
            
            story.append(Spacer(1, 12))
            
            # Skill Gap Suggestions
            if 'skill_gap_suggestions' in match_results:
                story.append(Paragraph("Skill Gap Suggestions", styles['Heading2']))
                for suggestion in match_results['skill_gap_suggestions']:
                    story.append(Paragraph(f"• {suggestion}", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
            
        except ImportError:
            st.warning("ReportLab not installed. Install with: pip install reportlab")
            return None
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            return None

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        color: #333333;
    }
    .strength-card {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        color: #155724;
    }
    .improvement-card {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        color: #856404;
    }
    .skill-tag {
        background-color: #e3f2fd;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
        color: #0d47a1;
        font-weight: 500;
    }
    .missing-skill-tag {
        background-color: #ffebee;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
        color: #c62828;
        font-weight: 500;
    }
    /* Ensure all text in cards is readable */
    .metric-card strong {
        color: #1f77b4;
    }
    .metric-card em {
        color: #666666;
    }
    .metric-card small {
        color: #888888;
    }
    /* Streamlit text color overrides */
    .stMarkdown, .stText {
        color: #333333 !important;
    }
    /* Ensure links are visible */
    .metric-card a {
        color: #1f77b4 !important;
        text-decoration: underline;
    }
    .metric-card a:hover {
        color: #0d47a1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🧩 Resume AI Matcher Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced AI-powered resume analysis and job matching platform</p>', unsafe_allow_html=True)
    
    # Initialize advanced components
    parser = AdvancedResumeParser()
    ai_matcher = AdvancedAIMatcher()
    explainable_matcher = ExplainableAIMatcher()
    pdf_generator = PDFGenerator()
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📄 Resume Upload", "💼 Job Description", "🤖 AI Analysis"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">📄 Resume Upload & Parsing</h2>', unsafe_allow_html=True)
        
        # File upload with validation
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT (max 10MB)"
        )
        
        if uploaded_file is not None:
            # File validation
            if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                st.error("File too large. Please upload a file smaller than 10MB.")
            else:
                # Store uploaded file bytes in session state
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                st.session_state.uploaded_file_bytes = file_bytes
                st.session_state.uploaded_file_name = uploaded_file.name
                
                with st.spinner("Parsing your resume with AI..."):
                    # Extract and parse
                    text = parser.extract_text_from_file(uploaded_file)
                    if text:
                        resume_data = parser.parse_resume_with_ai(text)
                        st.session_state.resume_data = resume_data
                        
                        st.success("✅ Resume parsed successfully!")
                        
                        # Display parsed data in a clean format
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown('<h3 style="color: #1f77b4;">👤 Personal Information</h3>', unsafe_allow_html=True)
                            st.markdown(f"""
                            <div class="metric-card">
                                <strong>Name:</strong> {resume_data['name'] or 'Not detected'}<br>
                                <strong>Email:</strong> {resume_data['email'] or 'Not detected'}<br>
                                <strong>Phone:</strong> {resume_data['phone'] or 'Not detected'}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if resume_data['skills']:
                                st.markdown('<h3 style="color: #1f77b4;">🛠️ Skills Detected</h3>', unsafe_allow_html=True)
                                skills_html = ""
                                for skill in resume_data['skills']:
                                    skills_html += f'<span class="skill-tag">{skill}</span>'
                                st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            if resume_data['experience']:
                                st.markdown('<h3 style="color: #1f77b4;">💼 Experience</h3>', unsafe_allow_html=True)
                                for i, exp in enumerate(resume_data['experience'][:3]):
                                    st.markdown(f"""
                                    <div class="metric-card">
                                        <strong>{exp.get('role', 'N/A')}</strong><br>
                                        <em>{exp.get('company', 'N/A')}</em><br>
                                        <small>{exp.get('duration', 'N/A')}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            if resume_data['education']:
                                st.markdown('<h3 style="color: #1f77b4;">🎓 Education</h3>', unsafe_allow_html=True)
                                for edu in resume_data['education'][:2]:
                                    st.markdown(f"""
                                    <div class="metric-card">
                                        <strong>{edu.get('degree', 'N/A')}</strong><br>
                                        <em>{edu.get('institution', 'N/A')}</em><br>
                                        <small>{edu.get('year', 'N/A')}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Could not extract text from the file.")
    
    with tab2:
        st.markdown('<h2 class="sub-header">💼 Job Description</h2>', unsafe_allow_html=True)
        
        jd_option = st.radio(
            "Choose input method:",
            ["Generate with AI", "Upload JD", "Type JD"]
        )
        
        if jd_option == "Generate with AI":
            col_a, col_b = st.columns(2)
            with col_a:
                role = st.text_input("Job Role:", placeholder="e.g., Software Engineer")
            with col_b:
                industry = st.text_input("Industry:", placeholder="e.g., Technology")
            
            keywords = st.text_input("Key Requirements:", placeholder="e.g., Python, React, AWS, 3+ years")
            
            if st.button("🚀 Generate Job Description", type="primary", use_container_width=True):
                if role and keywords:
                    with st.spinner("Generating job description with AI..."):
                        generated_jd = ai_matcher.generate_job_description(role, keywords, industry)
                        st.session_state.job_description = generated_jd
                        st.success("✅ Job description generated!")
                        st.markdown('<h3 style="color: #1f77b4;">Generated Job Description</h3>', unsafe_allow_html=True)
                        st.text_area("Job Description", generated_jd, height=300, label_visibility="collapsed")
                else:
                    st.warning("Please provide role and keywords.")
        
        elif jd_option == "Upload JD":
            jd_file = st.file_uploader("Upload job description", type=['pdf', 'txt', 'docx'])
            if jd_file:
                text = parser.extract_text_from_file(jd_file)
                st.session_state.job_description = text
                st.markdown('<h3 style="color: #1f77b4;">Job Description</h3>', unsafe_allow_html=True)
                st.text_area("Job Description", text, height=300, label_visibility="collapsed")
        
        else:  # Type JD
            st.markdown('<h3 style="color: #1f77b4;">Enter Job Description</h3>', unsafe_allow_html=True)
            jd_text = st.text_area("Job Description", height=300, placeholder="Paste or type the job description here...", label_visibility="collapsed")
            if jd_text:
                st.session_state.job_description = jd_text
    
    with tab3:
        st.markdown('<h2 class="sub-header">🤖 AI Analysis</h2>', unsafe_allow_html=True)
        
        # Add explainable matching option
        analysis_type = st.radio(
            "Choose analysis type:",
            ["Standard Matching", "Explainable AI Analysis"],
            help="Standard: Basic match score. Explainable: Detailed phrase-level analysis with justifications."
        )
        
        if st.session_state.resume_data and st.session_state.job_description:
            if st.button("🎯 Start AI Analysis", type="primary", use_container_width=True):
                with st.spinner("Performing comprehensive AI analysis..."):
                    if analysis_type == "Explainable AI Analysis":
                        # Get raw resume text for explainable analysis
                        resume_text = ""
                        if st.session_state.resume_data:
                            # Reconstruct resume text from parsed data
                            resume_text = f"""
                            Name: {st.session_state.resume_data.get('name', '')}
                            Email: {st.session_state.resume_data.get('email', '')}
                            Phone: {st.session_state.resume_data.get('phone', '')}
                            
                            Skills: {', '.join(st.session_state.resume_data.get('skills', []))}
                            
                            Experience:
                            {chr(10).join([f"- {exp.get('role', '')} at {exp.get('company', '')} ({exp.get('duration', '')})" for exp in st.session_state.resume_data.get('experience', [])])}
                            
                            Education:
                            {chr(10).join([f"- {edu.get('degree', '')} from {edu.get('institution', '')}" for edu in st.session_state.resume_data.get('education', [])])}
                            """
                        
                        # Perform explainable matching
                        explainable_result = explainable_matcher.match_with_explanations(
                            resume_text,
                            st.session_state.job_description
                        )
                        
                        if explainable_result:
                            st.session_state.explainable_results = explainable_result
                            st.success("✅ Explainable analysis complete!")
                        else:
                            st.error("❌ Explainable analysis failed")
                    else:
                        # Standard matching
                        match_results = ai_matcher.match_resume_to_job(
                            st.session_state.resume_data,
                            st.session_state.job_description
                        )
                        st.session_state.match_results = match_results
                        
                        # Generate enhancement suggestions
                        enhanced_resume = ai_matcher.enhance_resume(
                            st.session_state.resume_data,
                            st.session_state.job_description
                        )
                        st.session_state.enhanced_resume = enhanced_resume
                        
                        st.success("✅ Standard analysis complete!")
                    
                    st.rerun()
        
        # Results Section
        if st.session_state.match_results:
            results = st.session_state.match_results
            
            # Main score display
            st.markdown('<h3 style="color: #1f77b4;">📊 Match Analysis Results</h3>', unsafe_allow_html=True)
            
            # Score metrics in cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <h2 style="color: #1f77b4; margin: 0;">{results['match_score']}%</h2>
                    <p style="margin: 0; font-weight: bold;">Overall Match</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Handle both old and new format
                if 'skills_match' in results and isinstance(results['skills_match'], dict):
                    skills_score = results['skills_match'].get('skills_score', 0)
                else:
                    # Calculate skills score from fallback method
                    resume_skills = set(skill.lower() for skill in st.session_state.resume_data.get('skills', []))
                    jd_skills = set()
                    common_skills = ['python', 'javascript', 'java', 'react', 'sql', 'aws', 'docker', 'machine learning', 'node.js', 'mongodb', 'kubernetes', 'git', 'html', 'css', 'agile', 'scrum', 'project management', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'spring boot', 'django', 'flask', 'express.js', 'vue.js', 'angular', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'jenkins', 'ci/cd', 'microservices', 'rest api', 'graphql', 'websockets', 'oauth', 'jwt', 'transformers', 'huggingface', 'langchain', 'whisper', 'whisperx', 'faiss', 'modal', 'llm', 'prompt engineering', 'fastapi', 'streamlit', 'spacy', 'openai', 'gemini', 'claude', 'bert', 'gpt', 'llama', 'vector store', 'embeddings', 'nlp', 'natural language processing', 'speech recognition', 'speaker detection', 'diarization', 's3']
                    
                    for skill in common_skills:
                        if skill in st.session_state.job_description.lower():
                            jd_skills.add(skill)
                    
                    if jd_skills:
                        skill_overlap = len(resume_skills.intersection(jd_skills))
                        skills_score = min(100, (skill_overlap / len(jd_skills)) * 100)
                    else:
                        skills_score = 50
                    
                    skills_score = max(10, skills_score)  # Minimum 10%
                
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <h2 style="color: #28a745; margin: 0;">{int(skills_score)}%</h2>
                    <p style="margin: 0; font-weight: bold;">Skills Match</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                experience_score = results.get('experience_score', 0)
                if experience_score == 0:
                    # Calculate experience score from fallback method
                    experience_score = 70 if st.session_state.resume_data.get('experience') else 30
                    experience_score = max(20, experience_score)  # Minimum 20%
                
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <h2 style="color: #ffc107; margin: 0;">{int(experience_score)}%</h2>
                    <p style="margin: 0; font-weight: bold;">Experience</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                education_score = results.get('education_score', 0)
                if education_score == 0:
                    # Calculate education score from fallback method
                    education_score = 80 if st.session_state.resume_data.get('education') else 40
                    education_score = max(30, education_score)  # Minimum 30%
                
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <h2 style="color: #17a2b8; margin: 0;">{int(education_score)}%</h2>
                    <p style="margin: 0; font-weight: bold;">Education</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Visual score gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=results['match_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Match Score", 'font': {'size': 24}},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed analysis in tabs
            analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs(["✅ Strengths", "⚠️ Improvements", "🧠 AI Reasoning", "🔧 Enhancements"])
            
            with analysis_tab1:
                st.markdown('<h4 style="color: #28a745;">✅ Candidate Strengths</h4>', unsafe_allow_html=True)
                for strength in results['strengths']:
                    st.markdown(f'<div class="strength-card">✅ {strength}</div>', unsafe_allow_html=True)
                
                # Handle matched skills display
                if 'skills_match' in results and isinstance(results['skills_match'], dict):
                    st.markdown('<h4 style="color: #28a745;">🎯 Matched Skills</h4>', unsafe_allow_html=True)
                    skills_html = ""
                    for skill in results['skills_match'].get('matched_skills', []):
                        skills_html += f'<span class="skill-tag">{skill}</span>'
                    st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)
            
            with analysis_tab2:
                st.markdown('<h4 style="color: #ffc107;">⚠️ Areas for Improvement</h4>', unsafe_allow_html=True)
                for improvement in results['missing']:
                    st.markdown(f'<div class="improvement-card">⚠️ {improvement}</div>', unsafe_allow_html=True)
                
                # Handle missing skills display
                if 'skills_match' in results and isinstance(results['skills_match'], dict):
                    st.markdown('<h4 style="color: #dc3545;">❌ Missing Skills</h4>', unsafe_allow_html=True)
                    skills_html = ""
                    for skill in results['skills_match'].get('missing_skills', []):
                        skills_html += f'<span class="missing-skill-tag">{skill}</span>'
                    st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)
                
                # Skill gap suggestions
                if 'skill_gap_suggestions' in results:
                    st.markdown('<h4 style="color: #17a2b8;">💡 Skill Gap Suggestions</h4>', unsafe_allow_html=True)
                    for suggestion in results['skill_gap_suggestions']:
                        st.markdown(f'<div class="metric-card">💡 {suggestion}</div>', unsafe_allow_html=True)
            
            with analysis_tab3:
                st.markdown('<h4 style="color: #6f42c1;">🧠 AI Reasoning</h4>', unsafe_allow_html=True)
                if 'reasoning' in results:
                    reasoning = results['reasoning']
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Skills Match:</strong> {reasoning.get('skills_match', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Experience Alignment:</strong> {reasoning.get('experience_alignment', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Project Relevance:</strong> {reasoning.get('project_relevance', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Bonus Factors:</strong> {reasoning.get('bonus_factors', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Learning resources
                if 'learning_resources' in results:
                    st.markdown('<h4 style="color: #17a2b8;">📚 Learning Resources</h4>', unsafe_allow_html=True)
                    for resource in results['learning_resources']:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>{resource['topic']}:</strong> <a href="{resource['link']}" target="_blank">{resource['link']}</a>
                        </div>
                        """, unsafe_allow_html=True)
            
            with analysis_tab4:
                if st.session_state.enhanced_resume:
                    enhanced = st.session_state.enhanced_resume
                    
                    st.markdown('<h4 style="color: #28a745;">🚀 Enhanced Bullet Points</h4>', unsafe_allow_html=True)
                    for bullet in enhanced['enhanced_bullet_points']:
                        st.markdown(f'<div class="strength-card">🚀 {bullet}</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<h4 style="color: #17a2b8;">💪 Power Verbs</h4>', unsafe_allow_html=True)
                        verbs_html = ""
                        for verb in enhanced['power_verbs']:
                            verbs_html += f'<span class="skill-tag">{verb}</span>'
                        st.markdown(f'<div>{verbs_html}</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<h4 style="color: #ffc107;">📈 Quantified Achievements</h4>', unsafe_allow_html=True)
                        for achievement in enhanced['quantified_achievements']:
                            st.markdown(f'<div class="improvement-card">📈 {achievement}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<h4 style="color: #6f42c1;">🔧 Skill Improvements</h4>', unsafe_allow_html=True)
                    for skill in enhanced['skill_improvements']:
                        st.markdown(f'<div class="metric-card">🔧 {skill}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<h4 style="color: #17a2b8;">📝 Formatting Suggestions</h4>', unsafe_allow_html=True)
                    for suggestion in enhanced['formatting_suggestions']:
                        st.markdown(f'<div class="metric-card">📝 {suggestion}</div>', unsafe_allow_html=True)
        
        # Explainable Results Section
        if st.session_state.explainable_results:
            explainable_result = st.session_state.explainable_results
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<h3 style="color: #1f77b4;">🔍 Explainable AI Analysis</h3>', unsafe_allow_html=True)
            
            # Add CSS for highlighting
            st.markdown(ResumeHighlighter.create_highlight_css(), unsafe_allow_html=True)
            
            # Main score display
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <h2 style="color: #1f77b4; margin: 0;">{explainable_result.match_score}%</h2>
                    <p style="margin: 0; font-weight: bold;">Explainable Match Score</p>
                </div>
                """, unsafe_allow_html=True)
                
                if explainable_result.summary:
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>AI Summary:</strong><br>
                        {explainable_result.summary}
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Display explanations
                ResumeHighlighter.display_explanations(explainable_result.explanations)
            
            # Suggestions and improvements
            if explainable_result.suggestions:
                st.markdown('<h4 style="color: #17a2b8;">💡 Improvement Suggestions</h4>', unsafe_allow_html=True)
                for suggestion in explainable_result.suggestions:
                    st.markdown(f'<div class="metric-card">💡 {suggestion}</div>', unsafe_allow_html=True)
            
            # Interactive resume highlighting
            st.markdown('<h4 style="color: #6f42c1;">📄 Highlighted Resume Analysis</h4>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6;">
                <p><strong>Legend:</strong></p>
                <ul>
                    <li><span style="background-color: #d4edda; color: #155724; padding: 2px 4px; border-radius: 3px;">Green</span> = Strong positive match</li>
                    <li><span style="background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 3px;">Yellow</span> = Neutral/minimal impact</li>
                    <li><span style="background-color: #f8d7da; color: #721c24; padding: 2px 4px; border-radius: 3px; text-decoration: line-through;">Red</span> = Negative mismatch</li>
                </ul>
                <p><em>Hover over highlighted phrases to see AI justifications.</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display highlighted resume analysis
            if st.session_state.resume_data:
                # Get the uploaded file bytes from session state
                uploaded_file_bytes = st.session_state.get('uploaded_file_bytes', None)
                
                # Create properly formatted highlighted resume with PDF annotations
                explainable_matcher.create_highlighted_pdf_display(
                    st.session_state.resume_data, 
                    explainable_result.explanations,
                    uploaded_file_bytes
                )
            
            # Download Report
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<h3 style="color: #1f77b4;">📥 Download Report</h3>', unsafe_allow_html=True)
            if st.button("📄 Generate PDF Report", type="secondary", use_container_width=True):
                pdf_buffer = pdf_generator.generate_match_report(
                    st.session_state.resume_data,
                    st.session_state.job_description,
                    results
                )
                
                if pdf_buffer:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer.getvalue(),
                        file_name=f"resume_match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.info("PDF generation requires ReportLab. Install with: pip install reportlab")

if __name__ == "__main__":
    main() 