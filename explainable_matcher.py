import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class PhraseExplanation:
    """Represents a phrase-level explanation with weight and justification"""
    phrase: str
    weight: int  # -10 to +10
    justification: str
    category: str  # 'positive', 'negative', 'neutral'
    resume_section: str  # 'experience', 'skills', 'education', etc.

@dataclass
class ExplainableMatchResult:
    """Structured result from explainable matching"""
    match_score: int  # 0-100
    explanations: List[PhraseExplanation]
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]

class ExplainableAIMatcher:
    """Advanced AI matcher with phrase-level explainability"""
    
    def __init__(self):
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.provider = os.getenv('AI_MODEL_PROVIDER', 'mistral')
    
    def create_explainable_prompt(self, resume_text: str, job_description: str) -> str:
        """Create a comprehensive prompt for explainable matching"""
        
        prompt = f"""
        You are an expert HR analyst evaluating a candidate's resume against a job description. 
        Your task is to provide a detailed, phrase-level analysis with explainable reasoning.

        **RESUME TEXT:**
        {resume_text}

        **JOB DESCRIPTION:**
        {job_description}

        **ANALYSIS REQUIREMENTS:**
        1. Compare each relevant phrase in the resume against job requirements
        2. Identify both positive matches (strengths) and negative mismatches (weaknesses)
        3. Assign weights from -10 to +10 for each phrase:
           - +10 to +7: Strong positive match
           - +6 to +3: Moderate positive match  
           - +2 to -2: Neutral/minimal impact
           - -3 to -6: Moderate negative mismatch
           - -7 to -10: Strong negative mismatch
        4. Provide clear, specific justifications for each weight
        5. Calculate overall match score (0-100) based on weighted analysis

        **OUTPUT FORMAT (JSON ONLY):**
        {{
            "match_score": 85,
            "explanations": [
                {{
                    "phrase": "Led development team of 5 engineers",
                    "weight": 8,
                    "justification": "Strong leadership experience aligns with team lead requirements",
                    "category": "positive",
                    "resume_section": "experience"
                }},
                {{
                    "phrase": "Basic knowledge of Python",
                    "weight": -3,
                    "justification": "Vague skill description; job requires advanced Python expertise",
                    "category": "negative", 
                    "resume_section": "skills"
                }}
            ],
            "summary": "Candidate shows strong leadership but lacks technical depth",
            "strengths": ["Leadership experience", "Project management"],
            "weaknesses": ["Vague technical skills", "Missing certifications"],
            "suggestions": ["Quantify technical achievements", "Add relevant certifications"]
        }}

        **IMPORTANT GUIDELINES:**
        - Be specific and actionable in justifications
        - Focus on phrases that significantly impact the match
        - Consider both technical skills and soft skills
        - Weight should reflect the phrase's importance to the job
        - Provide constructive feedback for improvement
        - Respond ONLY with valid JSON, no additional text

        Analyze the resume and provide your structured response:
        """
        
        return prompt
    
    def call_ai_api(self, prompt: str) -> str:
        """Call the configured AI API"""
        try:
            if self.provider == 'mistral' and self.mistral_api_key:
                return self._call_mistral(prompt)
            elif self.provider == 'openai' and self.openai_api_key:
                return self._call_openai(prompt)
            else:
                st.warning("⚠️ No AI API configured, using fallback analysis")
                return self._generate_fallback_response()
        except Exception as e:
            st.error(f"❌ AI API error: {e}")
            return self._generate_fallback_response()
    
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
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3  # Lower temperature for more consistent output
            )
            
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            return ""
    
    def _generate_fallback_response(self) -> str:
        """Generate a fallback response when AI is not available"""
        return json.dumps({
            "match_score": 75,
            "explanations": [
                {
                    "phrase": "Software development experience",
                    "weight": 6,
                    "justification": "General development experience is relevant",
                    "category": "positive",
                    "resume_section": "experience"
                },
                {
                    "phrase": "Team collaboration",
                    "weight": 4,
                    "justification": "Soft skills are valuable for team environments",
                    "category": "positive",
                    "resume_section": "experience"
                }
            ],
            "summary": "Candidate shows relevant background with room for improvement",
            "strengths": ["Development experience", "Teamwork"],
            "weaknesses": ["Limited specific technical details", "Missing certifications"],
            "suggestions": ["Add specific technical achievements", "Include relevant certifications"]
        })
    
    def parse_ai_response(self, response: str) -> Optional[ExplainableMatchResult]:
        """Parse and validate AI response"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Validate required fields
                if 'match_score' not in data or 'explanations' not in data:
                    raise ValueError("Missing required fields in AI response")
                
                # Convert explanations to PhraseExplanation objects
                explanations = []
                for exp in data.get('explanations', []):
                    explanation = PhraseExplanation(
                        phrase=exp.get('phrase', ''),
                        weight=exp.get('weight', 0),
                        justification=exp.get('justification', ''),
                        category=exp.get('category', 'neutral'),
                        resume_section=exp.get('resume_section', 'general')
                    )
                    explanations.append(explanation)
                
                return ExplainableMatchResult(
                    match_score=data.get('match_score', 0),
                    explanations=explanations,
                    summary=data.get('summary', ''),
                    strengths=data.get('strengths', []),
                    weaknesses=data.get('weaknesses', []),
                    suggestions=data.get('suggestions', [])
                )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            st.error(f"❌ Failed to parse AI response: {e}")
            return None
        
        return None
    
    def match_with_explanations(self, resume_text: str, job_description: str) -> Optional[ExplainableMatchResult]:
        """Main method to perform explainable matching"""
        
        # Create the prompt
        prompt = self.create_explainable_prompt(resume_text, job_description)
        
        # Call AI API
        with st.spinner("🤖 Performing explainable AI analysis..."):
            response = self.call_ai_api(prompt)
        
        if not response:
            st.error("❌ No response from AI API")
            return None
        
        # Parse the response
        result = self.parse_ai_response(response)
        
        if result is None:
            st.error("❌ Failed to parse AI response")
            return None
        
        return result
    
    def highlight_resume_text(self, resume_text: str, explanations: List[PhraseExplanation]) -> str:
        """Highlight phrases in resume text based on explanations"""
        highlighted_text = resume_text
        
        # Sort explanations by weight (most impactful first)
        sorted_explanations = sorted(explanations, key=lambda x: abs(x.weight), reverse=True)
        
        for explanation in sorted_explanations:
            phrase = explanation.phrase
            weight = explanation.weight
            
            # Determine CSS class based on weight
            if weight >= 5:
                css_class = "highlight-positive"
            elif weight >= 0:
                css_class = "highlight-neutral"
            else:
                css_class = "highlight-negative"
            
            # Create tooltip with justification
            tooltip = f'title="{explanation.justification}"'
            
            # Replace phrase with highlighted version
            highlighted_phrase = f'<span class="{css_class}" {tooltip}>{phrase}</span>'
            highlighted_text = highlighted_text.replace(phrase, highlighted_phrase)
        
        return highlighted_text

class ResumeHighlighter:
    """Utility class for highlighting resume text with explanations"""
    
    @staticmethod
    def create_highlight_css() -> str:
        """Create CSS for highlighting phrases"""
        return """
        <style>
        .highlight-positive {
            background-color: #d4edda;
            color: #155724;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
            cursor: help;
        }
        
        .highlight-neutral {
            background-color: #fff3cd;
            color: #856404;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
            cursor: help;
        }
        
        .highlight-negative {
            background-color: #f8d7da;
            color: #721c24;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
            cursor: help;
            text-decoration: line-through;
        }
        
        .explanation-card {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        
        .weight-indicator {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .weight-positive {
            background-color: #28a745;
            color: white;
        }
        
        .weight-negative {
            background-color: #dc3545;
            color: white;
        }
        
        .weight-neutral {
            background-color: #ffc107;
            color: black;
        }
        </style>
        """
    
    @staticmethod
    def display_explanations(explanations: List[PhraseExplanation]) -> None:
        """Display explanations in a structured format"""
        st.markdown("### 📊 Phrase-Level Analysis")
        
        # Group by category
        positive_explanations = [exp for exp in explanations if exp.weight > 0]
        negative_explanations = [exp for exp in explanations if exp.weight < 0]
        neutral_explanations = [exp for exp in explanations if exp.weight == 0]
        
        # Display positive explanations
        if positive_explanations:
            st.markdown("#### ✅ Strengths")
            for exp in sorted(positive_explanations, key=lambda x: x.weight, reverse=True):
                weight_class = "weight-positive" if exp.weight >= 5 else "weight-neutral"
                st.markdown(f"""
                <div class="explanation-card">
                    <strong>{exp.phrase}</strong>
                    <span class="weight-indicator {weight_class}">+{exp.weight}</span>
                    <br><em>{exp.justification}</em>
                    <br><small>Section: {exp.resume_section}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Display negative explanations
        if negative_explanations:
            st.markdown("#### ❌ Areas for Improvement")
            for exp in sorted(negative_explanations, key=lambda x: exp.weight):
                st.markdown(f"""
                <div class="explanation-card">
                    <strong>{exp.phrase}</strong>
                    <span class="weight-indicator weight-negative">{exp.weight}</span>
                    <br><em>{exp.justification}</em>
                    <br><small>Section: {exp.resume_section}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Display neutral explanations
        if neutral_explanations:
            st.markdown("#### ⚖️ Neutral Factors")
            for exp in neutral_explanations:
                st.markdown(f"""
                <div class="explanation-card">
                    <strong>{exp.phrase}</strong>
                    <span class="weight-indicator weight-neutral">{exp.weight}</span>
                    <br><em>{exp.justification}</em>
                    <br><small>Section: {exp.resume_section}</small>
                </div>
                """, unsafe_allow_html=True) 