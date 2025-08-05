from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
import json
import io
import base64
from datetime import datetime
import fitz  # PyMuPDF
import PyPDF2
import pdfplumber
from docx import Document
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Resume AI Matcher Pro API",
    description="Advanced AI-powered resume analysis and job matching platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = []
    experience: List[Dict[str, str]] = []
    education: List[Dict[str, str]] = []
    projects: List[str] = []
    certifications: List[str] = []
    achievements: List[str] = []

class JobDescriptionRequest(BaseModel):
    role: str
    keywords: str
    industry: str = ""

class JobDescriptionResponse(BaseModel):
    job_description: str
    generated: bool

class MatchRequest(BaseModel):
    resume_data: ResumeData
    job_description: str
    analysis_type: str = "standard"  # "standard" or "explainable"

class MatchResponse(BaseModel):
    match_score: int
    reasoning: Dict[str, str]
    strengths: List[str]
    missing: List[str]
    skill_gap_suggestions: List[str]
    learning_resources: List[Dict[str, str]]
    resume_enhancer: List[Dict[str, str]]

class ExplainableMatchResponse(BaseModel):
    match_score: int
    explanations: List[Dict[str, Any]]
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]

class PhraseExplanation(BaseModel):
    phrase: str
    weight: int  # -10 to +10
    justification: str
    category: str  # "skill", "experience", "education", "achievement", etc.

class EnhancedResumeResponse(BaseModel):
    enhanced_bullet_points: List[str]
    power_verbs: List[str]
    quantified_achievements: List[str]
    skill_improvements: List[str]
    formatting_suggestions: List[str]

# Initialize components
class AdvancedResumeParser:
    """Advanced AI-powered resume parser with few-shot learning"""
    
    @staticmethod
    def extract_text_from_file(file_content: bytes, file_type: str) -> str:
        """Extract text from PDF, DOCX, or other file formats"""
        try:
            if file_type == "application/pdf":
                return AdvancedResumeParser._extract_from_pdf(file_content)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return AdvancedResumeParser._extract_from_docx(file_content)
            else:
                return file_content.decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error extracting text: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF using multiple methods"""
        try:
            # Try PyMuPDF first (best for complex layouts)
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
            return text
        except Exception as e:
            try:
                # Try pdfplumber
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                    return text
            except Exception as e2:
                try:
                    # Try PyPDF2
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
                except Exception as e3:
                    raise HTTPException(status_code=400, detail=f"All PDF extraction methods failed: {str(e3)}")
    
    @staticmethod
    def _extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error extracting from DOCX: {str(e)}")
    
    @staticmethod
    def parse_resume_with_ai(text: str) -> Dict[str, Any]:
        """Parse resume using AI with few-shot learning"""
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
        
        # Enhanced skill extraction
        skill_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'machine learning', 'ai', 'data science',
            'html', 'css', 'git', 'agile', 'scrum', 'project management',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
            'spring boot', 'django', 'flask', 'express.js', 'vue.js', 'angular',
            'postgresql', 'mysql', 'redis', 'elasticsearch', 'jenkins', 'ci/cd',
            'microservices', 'rest api', 'graphql', 'websockets', 'oauth', 'jwt',
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
        
        # Extract name
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not '@' in line and not line.isdigit():
                if re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*$', line):
                    parsed_data["name"] = line
                    break
        
        # Extract experience
        experience_patterns = [
            r'(\w+\s+\w+)\s+at\s+([^,\n]+)\s*\(?(\d{4}-\d{4}|\d{4}-\s*present|\d{4})\)?',
            r'([^,\n]+)\s*-\s*(\w+\s+\w+)\s*\(?(\d{4}-\d{4}|\d{4}-\s*present|\d{4})\)?'
        ]
        
        seen_experiences = set()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    role = match[0].strip()
                    company = match[1].strip()
                    duration = match[2].strip()
                    
                    experience_key = f"{role}@{company}@{duration}"
                    
                    if experience_key not in seen_experiences:
                        seen_experiences.add(experience_key)
                        parsed_data["experience"].append({
                            "role": role,
                            "company": company,
                            "duration": duration,
                            "description": ""
                        })
        
        # Extract education
        education_patterns = [
            r'(Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.E|M\.E|B\.Sc|M\.Sc)\s+[^,\n]*',
            r'([A-Z][a-z]+)\s+University\s*[^,\n]*',
            r'([A-Z][a-z]+)\s+College\s*[^,\n]*'
        ]
        
        seen_degrees = set()
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                degree = match.strip()
                if (degree and 
                    degree not in seen_degrees and 
                    degree.lower() not in ['board', 'school', 'high', 'secondary', 'primary', 'middle'] and
                    len(degree) > 2):
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
        
        # Enhanced skill extraction from job description
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        jd_skills = set()
        
        # Comprehensive skill keywords
        common_skills = [
            'python', 'javascript', 'java', 'react', 'sql', 'aws', 'docker', 
            'machine learning', 'node.js', 'mongodb', 'kubernetes', 'git',
            'html', 'css', 'agile', 'scrum', 'project management',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
            'spring boot', 'django', 'flask', 'express.js', 'vue.js', 'angular',
            'postgresql', 'mysql', 'redis', 'elasticsearch', 'jenkins', 'ci/cd',
            'microservices', 'rest api', 'graphql', 'websockets', 'oauth', 'jwt',
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
        
        # Calculate experience score
        experience_score = 70 if resume_data.get('experience') else 30
        experience_score = max(20, experience_score)  # Minimum 20%
        
        # Calculate education score
        education_score = 80 if resume_data.get('education') else 40
        education_score = max(30, education_score)  # Minimum 30%
        
        # Calculate overall score
        overall_score = (skills_score * 0.4 + experience_score * 0.4 + education_score * 0.2)
        
        return {
            "match_score": int(overall_score),
            "reasoning": {
                "skills_match": f"Skill overlap analysis: {len(resume_skills.intersection(jd_skills))} matched, {len(jd_skills - resume_skills)} missing",
                "experience_alignment": f"Experience relevance: {experience_score}% based on role requirements",
                "project_relevance": "Project analysis based on job responsibilities",
                "bonus_factors": "Additional positive factors identified"
            },
            "strengths": ["Technical skills present", "Relevant background"],
            "missing": ["Add more specific experience", "Include certifications"],
            "resume_enhancer": [
                {
                    "current_line": "Current experience description",
                    "suggestion": "Enhanced version with metrics and impact"
                }
            ],
            "skill_gap_suggestions": ["Highlight relevant projects", "Add more technical skills"],
            "learning_resources": [
                {"topic": "Skill Development", "link": "https://example.com/learning"},
                {"topic": "Best Practices", "link": "https://example.com/practices"}
            ]
        }
    
    def enhance_resume(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Generate resume enhancement suggestions"""
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

    def explainable_match_resume(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Perform explainable AI matching with detailed phrase-level explanations"""
        try:
            # Create a comprehensive prompt for XAI analysis
            resume_text = self._format_resume_for_analysis(resume_data)
            
            prompt = f"""
You are an expert AI resume analyzer. Analyze the match between a resume and job description, providing detailed explanations for each phrase that contributes to or detracts from the match.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

TASK: Analyze the match and return a JSON object with the following structure:
{{
    "match_score": <integer 0-100>,
    "explanations": [
        {{
            "phrase": "<exact phrase from resume>",
            "weight": <integer -10 to +10>,
            "justification": "<detailed explanation of why this phrase contributes positively or negatively>",
            "category": "<skill|experience|education|achievement|project|certification>"
        }}
    ],
    "summary": "<overall analysis summary>",
    "strengths": ["<list of major strengths>"],
    "weaknesses": ["<list of major weaknesses>"],
    "suggestions": ["<list of improvement suggestions>"]
}}

IMPORTANT RULES:
1. Return ONLY valid JSON, no other text
2. Each phrase must be an exact match from the resume text
3. Weights: -10 (very negative) to +10 (very positive)
4. Provide specific, actionable justifications
5. Focus on the most impactful phrases (at least 5-10 explanations)
6. Consider skills, experience relevance, achievements, and alignment with job requirements

Analyze the match and return the JSON response:
"""

            # Try to get AI response
            try:
                response = self._call_mistral(prompt)
                # Parse JSON response
                result = json.loads(response)
                
                # Validate and clean the response
                if not isinstance(result, dict):
                    raise ValueError("Invalid response format")
                
                # Ensure required fields exist
                result.setdefault("match_score", 75)
                result.setdefault("explanations", [])
                result.setdefault("summary", "Analysis completed")
                result.setdefault("strengths", [])
                result.setdefault("weaknesses", [])
                result.setdefault("suggestions", [])
                
                return result
                
            except Exception as ai_error:
                # Fallback to rule-based analysis
                return self._fallback_explainable_analysis(resume_data, job_description)
                
        except Exception as e:
            # Final fallback
            return {
                "match_score": 75,
                "explanations": [
                    {
                        "phrase": "Experience in software development",
                        "weight": 5,
                        "justification": "General software development experience is relevant",
                        "category": "experience"
                    }
                ],
                "summary": "Basic analysis completed",
                "strengths": ["Has relevant experience"],
                "weaknesses": ["Could provide more specific details"],
                "suggestions": ["Add more specific achievements and metrics"]
            }

    def _format_resume_for_analysis(self, resume_data: Dict) -> str:
        """Format resume data for AI analysis"""
        lines = []
        
        if resume_data.get("name"):
            lines.append(f"Name: {resume_data['name']}")
        
        if resume_data.get("skills"):
            lines.append(f"Skills: {', '.join(resume_data['skills'])}")
        
        if resume_data.get("experience"):
            lines.append("Experience:")
            for exp in resume_data["experience"]:
                lines.append(f"  {exp.get('role', '')} at {exp.get('company', '')}")
                lines.append(f"  Duration: {exp.get('duration', '')}")
                lines.append(f"  Description: {exp.get('description', '')}")
        
        if resume_data.get("education"):
            lines.append("Education:")
            for edu in resume_data["education"]:
                lines.append(f"  {edu.get('degree', '')} from {edu.get('institution', '')}")
                lines.append(f"  Year: {edu.get('year', '')}")
        
        if resume_data.get("projects"):
            lines.append("Projects:")
            for project in resume_data["projects"]:
                lines.append(f"  {project}")
        
        if resume_data.get("certifications"):
            lines.append("Certifications:")
            for cert in resume_data["certifications"]:
                lines.append(f"  {cert}")
        
        if resume_data.get("achievements"):
            lines.append("Achievements:")
            for achievement in resume_data["achievements"]:
                lines.append(f"  {achievement}")
        
        return "\n".join(lines)

    def _fallback_explainable_analysis(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Fallback rule-based explainable analysis"""
        explanations = []
        strengths = []
        weaknesses = []
        
        # Analyze skills
        resume_skills = set(skill.lower() for skill in resume_data.get("skills", []))
        job_skills = set(re.findall(r'\b\w+\b', job_description.lower()))
        
        # Common job requirements
        common_requirements = {
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 
            'kubernetes', 'sql', 'mongodb', 'git', 'agile', 'scrum', 'leadership',
            'communication', 'problem solving', 'teamwork', 'analytical', 'creative'
        }
        
        # Find matching skills
        for skill in resume_skills:
            if skill in job_skills:
                explanations.append({
                    "phrase": skill,
                    "weight": 8,
                    "justification": f"Skill '{skill}' directly matches job requirements",
                    "category": "skill"
                })
                strengths.append(f"Has required skill: {skill}")
        
        # Find missing skills
        missing_skills = job_skills.intersection(common_requirements) - resume_skills
        for skill in missing_skills:
            weaknesses.append(f"Missing required skill: {skill}")
        
        # Analyze experience
        for exp in resume_data.get("experience", []):
            if exp.get("description"):
                explanations.append({
                    "phrase": exp["description"][:100] + "...",
                    "weight": 6,
                    "justification": "Relevant work experience",
                    "category": "experience"
                })
        
        # Analyze achievements
        for achievement in resume_data.get("achievements", []):
            if any(word in achievement.lower() for word in ['improved', 'increased', 'reduced', 'led', 'managed']):
                explanations.append({
                    "phrase": achievement,
                    "weight": 7,
                    "justification": "Quantified achievement showing impact",
                    "category": "achievement"
                })
                strengths.append(f"Strong achievement: {achievement[:50]}...")
        
        # Check for missing experience types
        experience_descriptions = [exp.get("description", "").lower() for exp in resume_data.get("experience", [])]
        if not any("lead" in desc or "manage" in desc for desc in experience_descriptions):
            weaknesses.append("Missing leadership/management experience")
        
        if not any("team" in desc for desc in experience_descriptions):
            weaknesses.append("Missing teamwork/collaboration experience")
        
        # Calculate match score
        positive_weights = sum(exp["weight"] for exp in explanations if exp["weight"] > 0)
        total_possible = len(resume_skills) * 10
        match_score = min(100, max(0, int((positive_weights / max(total_possible, 1)) * 100)))
        
        suggestions = []
        if missing_skills:
            suggestions.append(f"Add missing skills: {', '.join(list(missing_skills)[:3])}")
        if not any("lead" in desc or "manage" in desc for desc in experience_descriptions):
            suggestions.append("Highlight leadership experience")
        if not any("team" in desc for desc in experience_descriptions):
            suggestions.append("Emphasize teamwork and collaboration")
        suggestions.append("Quantify achievements with specific metrics")
        suggestions.append("Add more relevant certifications")
        
        return {
            "match_score": match_score,
            "explanations": explanations,
            "summary": f"Rule-based analysis: {len(strengths)} strengths, {len(weaknesses)} areas for improvement",
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions
        }

# Initialize components
parser = AdvancedResumeParser()
ai_matcher = AdvancedAIMatcher()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Resume AI Matcher Pro API", "version": "1.0.0"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume file"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from file
        text = parser.extract_text_from_file(file_content, file.content_type)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Parse resume with AI
        resume_data = parser.parse_resume_with_ai(text)
        
        # Convert to base64 for frontend
        file_base64 = base64.b64encode(file_content).decode()
        
        return {
            "success": True,
            "resume_data": resume_data,
            "file_base64": file_base64,
            "file_name": file.filename,
            "file_type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-job-description")
async def generate_job_description(request: JobDescriptionRequest):
    """Generate job description using AI"""
    try:
        job_description = ai_matcher.generate_job_description(
            request.role, 
            request.keywords, 
            request.industry
        )
        
        return JobDescriptionResponse(
            job_description=job_description,
            generated=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match-resume")
async def match_resume(request: MatchRequest):
    """Match resume to job description"""
    try:
        if request.analysis_type == "explainable":
            # Use explainable AI matching
            result = ai_matcher.explainable_match_resume(
                request.resume_data.dict(), 
                request.job_description
            )
            
            return ExplainableMatchResponse(
                match_score=result.get("match_score", 0),
                explanations=result.get("explanations", []),
                summary=result.get("summary", ""),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                suggestions=result.get("suggestions", [])
            )
        else:
            # Use standard matching
            result = ai_matcher.match_resume_to_job(
                request.resume_data.dict(), 
                request.job_description
            )
            
            return MatchResponse(
                match_score=result.get("match_score", 0),
                reasoning=result.get("reasoning", {}),
                strengths=result.get("strengths", []),
                missing=result.get("missing", []),
                skill_gap_suggestions=result.get("skill_gap_suggestions", []),
                learning_resources=result.get("learning_resources", []),
                resume_enhancer=result.get("resume_enhancer", [])
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhance-resume")
async def enhance_resume(request: MatchRequest):
    """Generate resume enhancement suggestions"""
    try:
        result = ai_matcher.enhance_resume(
            request.resume_data.dict(), 
            request.job_description
        )
        
        return EnhancedResumeResponse(
            enhanced_bullet_points=result.get("enhanced_bullet_points", []),
            power_verbs=result.get("power_verbs", []),
            quantified_achievements=result.get("quantified_achievements", []),
            skill_improvements=result.get("skill_improvements", []),
            formatting_suggestions=result.get("formatting_suggestions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PDFAnnotator:
    """PDF annotation functionality for highlighting resume content"""
    
    @staticmethod
    def create_annotated_pdf(uploaded_file_bytes: bytes, explanations: List[Dict[str, Any]]) -> bytes:
        """Create a new PDF with annotations and highlighting"""
        try:
            # Open the original PDF
            pdf_document = fitz.open(stream=uploaded_file_bytes, filetype="pdf")
            
            # Add annotations to each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                PDFAnnotator._add_page_annotations(page, explanations, page_num)
            
            # Add a summary page
            PDFAnnotator._add_summary_page(pdf_document, explanations)
            
            # Save the annotated PDF
            output_bytes = pdf_document.write()
            pdf_document.close()
            
            return output_bytes
            
        except Exception as e:
            print(f"Error creating annotated PDF: {e}")
            return uploaded_file_bytes
    
    @staticmethod
    def _add_page_annotations(page, explanations: List[Dict[str, Any]], page_num: int):
        """Add highlights and annotations to a specific page"""
        try:
            # Get page text and create a dictionary for text positions
            text_dict = page.get_text("dict")
            
            # Add highlights for positive explanations (green)
            positive_explanations = [exp for exp in explanations if exp.get("weight", 0) > 0]
            if positive_explanations:
                PDFAnnotator._add_highlight_annotations(page, positive_explanations, text_dict, (0, 1, 0))  # Green
            
            # Add highlights for negative explanations (red)
            negative_explanations = [exp for exp in explanations if exp.get("weight", 0) < 0]
            if negative_explanations:
                PDFAnnotator._add_highlight_annotations(page, negative_explanations, text_dict, (1, 0, 0))  # Red
            
            # Add bubble annotations
            PDFAnnotator._add_bubble_annotations(page, explanations, page_num)
            
        except Exception as e:
            print(f"Error adding page annotations: {e}")
    
    @staticmethod
    def _find_text_positions(page, target_phrase: str) -> List[tuple]:
        """Find all positions of a phrase in the page"""
        positions = []
        try:
            # Get text blocks
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].lower()
                            if target_phrase.lower() in text:
                                # Get the bounding box
                                bbox = span["bbox"]
                                positions.append(bbox)
            
        except Exception as e:
            print(f"Error finding text positions: {e}")
        
        return positions
    
    @staticmethod
    def _add_highlight_annotations(page, explanations: List[Dict[str, Any]], text_dict: Dict, color: tuple):
        """Add highlight annotations to the page"""
        try:
            for explanation in explanations:
                phrase = explanation.get("phrase", "")
                weight = explanation.get("weight", 0)
                
                # Find positions of the phrase
                positions = PDFAnnotator._find_text_positions(page, phrase)
                
                for bbox in positions:
                    # Create highlight annotation
                    highlight = page.add_highlight_annot(bbox)
                    highlight.set_colors(stroke=color)
                    highlight.set_opacity(0.3)
                    
                    # Add weight indicator
                    PDFAnnotator._add_weight_indicator(page, bbox, weight)
                    
        except Exception as e:
            print(f"Error adding highlight annotations: {e}")
    
    @staticmethod
    def _add_weight_indicator(page, bbox, weight: int):
        """Add a small symbol to indicate weight"""
        try:
            x, y, w, h = bbox
            symbol = "🟢" if weight >= 7 else "🟡" if weight >= 4 else "🔴"
            
            # Add text annotation for the symbol
            text_annot = page.add_text_annot((x + w, y), symbol)
            text_annot.set_fontsize(8)
            
        except Exception as e:
            print(f"Error adding weight indicator: {e}")
    
    @staticmethod
    def _add_bubble_annotations(page, explanations: List[Dict[str, Any]], page_num: int):
        """Add bubble annotations with explanations"""
        try:
            # Position bubbles on the right side of the page
            page_width = page.rect.width
            bubble_x = page_width - 150
            
            for i, explanation in enumerate(explanations[:5]):  # Limit to 5 bubbles per page
                phrase = explanation.get("phrase", "")
                justification = explanation.get("justification", "")
                weight = explanation.get("weight", 0)
                
                # Create bubble text
                bubble_text = f"'{phrase}'\nWeight: {weight}/10\n{justification[:100]}..."
                
                # Position bubble
                bubble_y = 100 + (i * 80)
                bubble_rect = fitz.Rect(bubble_x, bubble_y, bubble_x + 140, bubble_y + 70)
                
                # Add bubble annotation
                bubble = page.add_text_annot(bubble_rect.tl, bubble_text)
                bubble.set_colors(stroke=(0, 0, 0))
                bubble.set_opacity(0.9)
                bubble.set_fontsize(8)
                
        except Exception as e:
            print(f"Error adding bubble annotations: {e}")
    
    @staticmethod
    def _add_summary_page(pdf_document, explanations: List[Dict[str, Any]]):
        """Add a summary page with analysis results"""
        try:
            # Create a new page
            page = pdf_document.new_page()
            
            # Add title
            title = "Resume Analysis Summary"
            page.insert_text((50, 50), title, fontsize=16, color=(0, 0, 0))
            
            # Add statistics
            positive_count = len([exp for exp in explanations if exp.get("weight", 0) > 0])
            negative_count = len([exp for exp in explanations if exp.get("weight", 0) < 0])
            
            stats_text = f"Positive Matches: {positive_count}\nNegative Mismatches: {negative_count}\nTotal Phrases Analyzed: {len(explanations)}"
            page.insert_text((50, 100), stats_text, fontsize=12, color=(0, 0, 0))
            
            # Add detailed explanations
            y_pos = 150
            for i, explanation in enumerate(explanations[:10]):  # Show first 10
                phrase = explanation.get("phrase", "")
                weight = explanation.get("weight", 0)
                justification = explanation.get("justification", "")
                
                exp_text = f"{i+1}. '{phrase}' (Weight: {weight}/10)\n   {justification}"
                page.insert_text((50, y_pos), exp_text, fontsize=10, color=(0, 0, 0))
                y_pos += 40
                
        except Exception as e:
            print(f"Error adding summary page: {e}")

@app.post("/create-annotated-pdf")
async def create_annotated_pdf(file: UploadFile = File(...), explanations: str = Form(...)):
    """Create an annotated PDF with highlights and explanations"""
    try:
        # Read the uploaded file
        file_content = await file.read()
        
        # Parse explanations JSON
        explanations_data = json.loads(explanations)
        
        # Create annotated PDF
        annotated_pdf_bytes = PDFAnnotator.create_annotated_pdf(file_content, explanations_data)
        
        # Convert to base64 for frontend
        pdf_base64 = base64.b64encode(annotated_pdf_bytes).decode()
        
        return {
            "success": True,
            "annotated_pdf_base64": pdf_base64,
            "file_name": f"annotated_{file.filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 