import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF
import io
import base64
from datetime import datetime

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
    
    def create_highlighted_resume_display(self, resume_data: Dict, explanations: List[PhraseExplanation], uploaded_file_bytes=None) -> None:
        """Display the original PDF with bubble annotations"""
        import streamlit as st
        
        st.markdown("### 📄 Original Resume with AI Annotations")
        st.markdown("*Bubble highlights show AI analysis of your uploaded resume*")
        
        if uploaded_file_bytes is not None:
            # Display the original uploaded file
            self.display_original_pdf_with_annotations(uploaded_file_bytes, explanations)
        else:
            # Fallback to text display if no file
            st.warning("No original file available. Showing text analysis.")
            self.display_text_with_annotations(explanations)
        
        # Add legend
        st.markdown("---")
        st.markdown("""
        **Annotation Legend:**
        - 🟢 **Green bubbles** = Excellent match for the job
        - 🟡 **Yellow bubbles** = Good but could be stronger
        - 🔴 **Red bubbles** = Needs improvement or irrelevant
        - *Hover over bubbles to see detailed AI feedback*
        """)
    
    def display_original_pdf_with_annotations(self, uploaded_file_bytes, explanations: List[PhraseExplanation]) -> None:
        """Display the original PDF with overlay annotations"""
        import streamlit as st
        import base64
        import fitz  # PyMuPDF
        
        try:
            # Convert PDF to image for display
            pdf_document = fitz.open(stream=uploaded_file_bytes, filetype="pdf")
            
            if len(pdf_document) == 0:
                st.error("PDF document is empty or corrupted")
                return
            
            # Get the first page
            page = pdf_document[0]
            
            # Convert to image with better quality
            zoom = 1.5  # Adjust zoom for better quality
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to base64 for display
            img_base64 = base64.b64encode(img_data).decode()
            
            # Display PDF first
            st.markdown(f"""
            <div style="position: relative; display: inline-block; margin: 20px 0; max-width: 100%;">
                <img src="data:image/png;base64,{img_base64}" 
                     style="max-width: 100%; height: auto; border: 3px solid #3498db; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: block;"
                     alt="Resume with annotations">
            </div>
            """, unsafe_allow_html=True)
            
            pdf_document.close()
            
            # Display annotations separately using Streamlit components
            st.markdown("### 🔍 AI Analysis Annotations")
            st.markdown("*Hover over each annotation to see detailed AI feedback*")
            
            # Create annotation display using Streamlit components
            self.display_annotations_with_streamlit(explanations)
            
        except Exception as e:
            st.error(f"Error displaying PDF: {e}")
            st.info("Falling back to text display...")
            # Fallback to text display
            self.display_text_with_annotations(explanations)
    
    def display_annotations_with_streamlit(self, explanations: List[PhraseExplanation]) -> None:
        """Display annotations using native Streamlit components"""
        import streamlit as st
        
        # Group explanations by weight
        positive_explanations = [exp for exp in explanations if exp.weight >= 5]
        neutral_explanations = [exp for exp in explanations if 0 <= exp.weight < 5]
        negative_explanations = [exp for exp in explanations if exp.weight < 0]
        
        # Display positive annotations
        if positive_explanations:
            st.markdown("#### 🟢 **Strong Matches**")
            for exp in positive_explanations[:5]:  # Show top 5
                with st.expander(f"✅ {exp.phrase} (+{exp.weight})", expanded=False):
                    st.markdown(f"**AI Analysis:** {exp.justification}")
                    st.markdown(f"**Category:** {exp.category}")
                    st.markdown(f"**Section:** {exp.resume_section}")
        
        # Display neutral annotations
        if neutral_explanations:
            st.markdown("#### 🟡 **Moderate Matches**")
            for exp in neutral_explanations[:3]:  # Show top 3
                with st.expander(f"⚠️ {exp.phrase} (+{exp.weight})", expanded=False):
                    st.markdown(f"**AI Analysis:** {exp.justification}")
                    st.markdown(f"**Category:** {exp.category}")
                    st.markdown(f"**Section:** {exp.resume_section}")
        
        # Display negative annotations
        if negative_explanations:
            st.markdown("#### 🔴 **Areas for Improvement**")
            for exp in negative_explanations[:3]:  # Show top 3
                with st.expander(f"❌ {exp.phrase} ({exp.weight})", expanded=False):
                    st.markdown(f"**AI Analysis:** {exp.justification}")
                    st.markdown(f"**Category:** {exp.category}")
                    st.markdown(f"**Section:** {exp.resume_section}")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Strong Matches", len(positive_explanations), "🟢")
        with col2:
            st.metric("Moderate Matches", len(neutral_explanations), "🟡")
        with col3:
            st.metric("Needs Improvement", len(negative_explanations), "🔴")
    
    def display_text_with_annotations(self, explanations: List[PhraseExplanation]) -> None:
        """Display text-based resume with annotations as fallback"""
        import streamlit as st
        
        st.markdown("### 📄 Resume Analysis (Text View)")
        
        # Create a simple text display with annotations
        annotation_css = """
        <style>
        .text-annotation {
            display: inline-block;
            margin: 2px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            cursor: help;
        }
        
        .text-positive {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #28a745;
        }
        
        .text-neutral {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffc107;
        }
        
        .text-negative {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #dc3545;
            text-decoration: line-through;
        }
        </style>
        """
        
        # Display explanations as text annotations
        st.markdown(annotation_css, unsafe_allow_html=True)
        
        st.markdown("**AI Analysis Results:**")
        
        positive_explanations = [exp for exp in explanations if exp.weight >= 5]
        neutral_explanations = [exp for exp in explanations if 0 <= exp.weight < 5]
        negative_explanations = [exp for exp in explanations if exp.weight < 0]
        
        if positive_explanations:
            st.markdown("**✅ Strong Matches:**")
            for exp in positive_explanations:
                st.markdown(f"""
                <span class="text-annotation text-positive" title="{exp.justification}">
                    🟢 {exp.phrase} (+{exp.weight})
                </span>
                """, unsafe_allow_html=True)
        
        if neutral_explanations:
            st.markdown("**🟡 Moderate Matches:**")
            for exp in neutral_explanations:
                st.markdown(f"""
                <span class="text-annotation text-neutral" title="{exp.justification}">
                    🟡 {exp.phrase} ({exp.weight:+d})
                </span>
                """, unsafe_allow_html=True)
        
        if negative_explanations:
            st.markdown("**❌ Areas for Improvement:**")
            for exp in negative_explanations:
                st.markdown(f"""
                <span class="text-annotation text-negative" title="{exp.justification}">
                    🔴 {exp.phrase} ({exp.weight:+d})
                </span>
                """, unsafe_allow_html=True)
    
    def create_annotation_overlay(self, explanations: List[PhraseExplanation]) -> str:
        """Create CSS overlay for annotations"""
        
        # Create annotation CSS
        annotation_css = """
        <style>
        .annotation-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }
        
        .annotation-bubble {
            position: absolute;
            background-color: rgba(40, 167, 69, 0.95);
            color: white;
            border: 3px solid #28a745;
            border-radius: 20px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: bold;
            cursor: help;
            pointer-events: auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            z-index: 20;
            max-width: 200px;
            word-wrap: break-word;
            text-align: center;
        }
        
        .annotation-bubble.positive {
            background-color: rgba(40, 167, 69, 0.95);
            border-color: #28a745;
            color: white;
        }
        
        .annotation-bubble.neutral {
            background-color: rgba(255, 193, 7, 0.95);
            border-color: #ffc107;
            color: #000;
        }
        
        .annotation-bubble.negative {
            background-color: rgba(220, 53, 69, 0.95);
            border-color: #dc3545;
            color: white;
        }
        
        .annotation-tooltip {
            position: absolute;
            bottom: 120%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            white-space: normal;
            max-width: 250px;
            z-index: 30;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .annotation-bubble:hover .annotation-tooltip {
            opacity: 1;
        }
        
        .annotation-arrow {
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #2c3e50;
        }
        </style>
        """
        
        # Create annotation bubbles with better positioning
        annotation_html = '<div class="annotation-overlay">'
        
        # Smart positioning based on content type
        positions = [
            {"top": "10%", "left": "15%", "type": "skills"},
            {"top": "20%", "left": "25%", "type": "skills"},
            {"top": "30%", "left": "20%", "type": "skills"},
            {"top": "40%", "left": "30%", "type": "skills"},
            {"top": "50%", "left": "35%", "type": "skills"},
            {"top": "60%", "left": "25%", "type": "skills"},
            {"top": "70%", "left": "20%", "type": "experience"},
            {"top": "80%", "left": "30%", "type": "education"},
        ]
        
        for i, pos in enumerate(positions):
            if i < len(explanations):
                exp = explanations[i]
                weight = exp.weight
                
                if weight >= 5:
                    bubble_class = "positive"
                    emoji = "🟢"
                elif weight >= 0:
                    bubble_class = "neutral"
                    emoji = "🟡"
                else:
                    bubble_class = "negative"
                    emoji = "🔴"
                
                # Create shorter display text
                display_text = exp.phrase[:20] + "..." if len(exp.phrase) > 20 else exp.phrase
                
                annotation_html += f"""
                <div class="annotation-bubble {bubble_class}" 
                     style="top: {pos['top']}; left: {pos['left']};"
                     title="{exp.justification}">
                    {emoji} {display_text} ({weight:+d})
                    <div class="annotation-tooltip">
                        {exp.justification}
                        <div class="annotation-arrow"></div>
                    </div>
                </div>
                """
        
        annotation_html += '</div>'
        
        return annotation_css + annotation_html
    
    def build_resume_content(self, resume_data: Dict) -> str:
        """Build the actual resume content"""
        
        # Header
        name = resume_data.get('name', 'N/A')
        email = resume_data.get('email', 'N/A')
        phone = resume_data.get('phone', 'N/A')
        
        header = f"""
        <div style="margin-bottom: 25px;">
            <h1 style="color: #2c3e50; margin-bottom: 15px; font-size: 28px;">{name}</h1>
            <p style="margin: 8px 0; color: #7f8c8d;"><strong>Email:</strong> {email}</p>
            <p style="margin: 8px 0; color: #7f8c8d;"><strong>Phone:</strong> {phone}</p>
        </div>
        """
        
        # Skills Section
        skills = resume_data.get('skills', [])
        skills_section = ""
        if skills:
            skills_text = ", ".join(skills)
            skills_section = f"""
            <div style="margin-bottom: 25px;">
                <h2 style="color: #34495e; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">🛠️ Skills</h2>
                <p style="font-size: 16px; line-height: 1.6;">{skills_text}</p>
            </div>
            """
        
        # Experience Section
        experience = resume_data.get('experience', [])
        exp_section = ""
        if experience:
            exp_text = ""
            for exp in experience:
                role = exp.get('role', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('duration', 'N/A')
                exp_text += f"<p style='margin: 10px 0;'><strong>{role}</strong> at {company} ({duration})</p>"
            
            exp_section = f"""
            <div style="margin-bottom: 25px;">
                <h2 style="color: #34495e; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">💼 Experience</h2>
                {exp_text}
            </div>
            """
        else:
            exp_section = """
            <div style="margin-bottom: 25px;">
                <h2 style="color: #34495e; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">💼 Experience</h2>
                <p style="color: #e74c3c; font-style: italic;">No experience listed</p>
            </div>
            """
        
        # Education Section
        education = resume_data.get('education', [])
        edu_section = ""
        if education:
            edu_text = ""
            for edu in education:
                degree = edu.get('degree', 'N/A')
                institution = edu.get('institution', 'N/A')
                edu_text += f"<p style='margin: 10px 0;'><strong>{degree}</strong> from {institution}</p>"
            
            edu_section = f"""
            <div style="margin-bottom: 25px;">
                <h2 style="color: #34495e; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">🎓 Education</h2>
                {edu_text}
            </div>
            """
        else:
            edu_section = """
            <div style="margin-bottom: 25px;">
                <h2 style="color: #34495e; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">🎓 Education</h2>
                <p style="color: #e74c3c; font-style: italic;">No education listed</p>
            </div>
            """
        
        return header + skills_section + exp_section + edu_section
    
    def add_bubble_annotations(self, resume_content: str, explanations: List[PhraseExplanation]) -> str:
        """Add bubble annotations to the resume content"""
        
        # Create CSS for bubble annotations
        bubble_css = """
        <style>
        .bubble-annotation {
            position: relative;
            display: inline-block;
        }
        
        .bubble-positive {
            background-color: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
            border-radius: 20px;
            padding: 8px 15px;
            margin: 2px;
            font-weight: 600;
            cursor: help;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .bubble-neutral {
            background-color: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
            border-radius: 20px;
            padding: 8px 15px;
            margin: 2px;
            font-weight: 500;
            cursor: help;
            position: relative;
        }
        
        .bubble-negative {
            background-color: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
            border-radius: 20px;
            padding: 8px 15px;
            margin: 2px;
            font-weight: 600;
            cursor: help;
            text-decoration: line-through;
            position: relative;
        }
        
        .bubble-tooltip {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }
        
        .bubble-annotation:hover .bubble-tooltip {
            opacity: 1;
        }
        </style>
        """
        
        # Add bubble annotations
        annotated_content = resume_content
        
        for exp in explanations:
            phrase = exp.phrase
            weight = exp.weight
            justification = exp.justification
            
            # Determine bubble class
            if weight >= 5:
                bubble_class = "bubble-positive"
                emoji = "🟢"
            elif weight >= 0:
                bubble_class = "bubble-neutral"
                emoji = "🟡"
            else:
                bubble_class = "bubble-negative"
                emoji = "🔴"
            
            # Create bubble annotation
            bubble_html = f"""
            <span class="bubble-annotation">
                <span class="{bubble_class}" title="{justification}">
                    {emoji} {phrase} ({weight:+d})
                </span>
                <div class="bubble-tooltip">{justification}</div>
            </span>
            """
            
            # Replace phrase with bubble (case-insensitive)
            import re
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            annotated_content = pattern.sub(bubble_html, annotated_content)
        
        return bubble_css + annotated_content
    
    def build_annotated_resume_text(self, resume_data: Dict, explanations: List[PhraseExplanation]) -> str:
        """Build the full resume text with HTML annotations"""
        
        # Create a mapping of phrases to explanations
        phrase_explanations = {}
        for exp in explanations:
            phrase_explanations[exp.phrase.lower()] = exp
        
        # Build resume sections
        sections = []
        
        # Header
        name = resume_data.get('name', 'N/A')
        email = resume_data.get('email', 'N/A')
        phone = resume_data.get('phone', 'N/A')
        
        header = f"""
        <div style="margin-bottom: 20px;">
            <h2 style="color: #2c3e50; margin-bottom: 10px;">{self.highlight_phrase(name, phrase_explanations)}</h2>
            <p style="margin: 5px 0;"><strong>Email:</strong> {self.highlight_phrase(email, phrase_explanations)}</p>
            <p style="margin: 5px 0;"><strong>Phone:</strong> {self.highlight_phrase(phone, phrase_explanations)}</p>
        </div>
        """
        sections.append(header)
        
        # Skills Section
        skills = resume_data.get('skills', [])
        if skills:
            skills_text = ", ".join(skills)
            skills_section = f"""
            <div style="margin-bottom: 20px;">
                <h3 style="color: #34495e; margin-bottom: 10px;">🛠️ Skills</h3>
                <p>{self.highlight_phrase(skills_text, phrase_explanations)}</p>
            </div>
            """
            sections.append(skills_section)
        
        # Experience Section
        experience = resume_data.get('experience', [])
        if experience:
            exp_text = ""
            for exp in experience:
                role = exp.get('role', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('duration', 'N/A')
                exp_text += f"• {role} at {company} ({duration})<br>"
            
            exp_section = f"""
            <div style="margin-bottom: 20px;">
                <h3 style="color: #34495e; margin-bottom: 10px;">💼 Experience</h3>
                <p>{self.highlight_phrase(exp_text, phrase_explanations)}</p>
            </div>
            """
            sections.append(exp_section)
        else:
            exp_section = """
            <div style="margin-bottom: 20px;">
                <h3 style="color: #34495e; margin-bottom: 10px;">💼 Experience</h3>
                <p style="color: #e74c3c; font-style: italic;">No experience listed</p>
            </div>
            """
            sections.append(exp_section)
        
        # Education Section
        education = resume_data.get('education', [])
        if education:
            edu_text = ""
            for edu in education:
                degree = edu.get('degree', 'N/A')
                institution = edu.get('institution', 'N/A')
                edu_text += f"• {degree} from {institution}<br>"
            
            edu_section = f"""
            <div style="margin-bottom: 20px;">
                <h3 style="color: #34495e; margin-bottom: 10px;">🎓 Education</h3>
                <p>{self.highlight_phrase(edu_text, phrase_explanations)}</p>
            </div>
            """
            sections.append(edu_section)
        else:
            edu_section = """
            <div style="margin-bottom: 20px;">
                <h3 style="color: #34495e; margin-bottom: 10px;">🎓 Education</h3>
                <p style="color: #e74c3c; font-style: italic;">No education listed</p>
            </div>
            """
            sections.append(edu_section)
        
        return "".join(sections)
    
    def highlight_phrase(self, text: str, phrase_explanations: Dict) -> str:
        """Highlight phrases in text based on explanations"""
        highlighted_text = text
        
        # Sort explanations by weight (most impactful first)
        sorted_explanations = sorted(phrase_explanations.items(), key=lambda x: abs(x[1].weight), reverse=True)
        
        for phrase_lower, explanation in sorted_explanations:
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
            
            # Replace phrase with highlighted version (case-insensitive)
            import re
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            highlighted_phrase = f'<span class="{css_class}" {tooltip}>{phrase}</span>'
            highlighted_text = pattern.sub(highlighted_phrase, highlighted_text)
        
        return highlighted_text
    
    def display_highlighted_skills(self, skills: List[str], explanations: List[PhraseExplanation]) -> None:
        """Display skills with highlighting using Streamlit components"""
        import streamlit as st
        
        if not skills:
            st.markdown("*No skills listed*")
            return
        
        # Create a mapping of skill to explanation
        skill_explanations = {}
        for exp in explanations:
            # Match skills more flexibly
            for skill in skills:
                if skill.lower() in exp.phrase.lower() or exp.phrase.lower() in skill.lower():
                    skill_explanations[skill.lower()] = exp
                    break
        
        # Display skills in a clean format
        st.markdown("**Skills Analysis:**")
        
        # Group skills by impact
        positive_skills = []
        neutral_skills = []
        negative_skills = []
        no_analysis_skills = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in skill_explanations:
                exp = skill_explanations[skill_lower]
                if exp.weight >= 5:
                    positive_skills.append((skill, exp))
                elif exp.weight >= 0:
                    neutral_skills.append((skill, exp))
                else:
                    negative_skills.append((skill, exp))
            else:
                no_analysis_skills.append(skill)
        
        # Display positive skills
        if positive_skills:
            st.markdown("**✅ Strong Matches:**")
            for skill, exp in positive_skills:
                st.markdown(f"• **{skill}** (+{exp.weight}) - {exp.justification}")
        
        # Display neutral skills
        if neutral_skills:
            st.markdown("**🟡 Moderate Matches:**")
            for skill, exp in neutral_skills:
                st.markdown(f"• **{skill}** ({exp.weight}) - {exp.justification}")
        
        # Display negative skills
        if negative_skills:
            st.markdown("**❌ Areas for Improvement:**")
            for skill, exp in negative_skills:
                st.markdown(f"• ~~**{skill}**~~ ({exp.weight}) - {exp.justification}")
        
        # Display skills with no analysis
        if no_analysis_skills:
            st.markdown("**⚪ Other Skills:**")
            for skill in no_analysis_skills:
                st.markdown(f"• **{skill}**")
        
        # Summary
        total_skills = len(skills)
        analyzed_skills = len(positive_skills) + len(neutral_skills) + len(negative_skills)
        st.markdown(f"---")
        st.markdown(f"**Summary:** {analyzed_skills}/{total_skills} skills analyzed")

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
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 600;
            cursor: help;
            border: 1px solid #28a745;
            display: inline-block;
            margin: 1px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .highlight-neutral {
            background-color: #fff3cd;
            color: #856404;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 500;
            cursor: help;
            border: 1px solid #ffc107;
            display: inline-block;
            margin: 1px;
        }
        
        .highlight-negative {
            background-color: #f8d7da;
            color: #721c24;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 600;
            cursor: help;
            text-decoration: line-through;
            border: 1px solid #dc3545;
            display: inline-block;
            margin: 1px;
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
    
    def create_annotated_pdf(self, uploaded_file_bytes: bytes, explanations: List[PhraseExplanation]) -> bytes:
        """Create a new PDF with actual annotations and highlighting"""
        try:
            # Open the original PDF
            pdf_document = fitz.open(stream=uploaded_file_bytes, filetype="pdf")
            
            if len(pdf_document) == 0:
                st.error("PDF document is empty or corrupted")
                return None
            
            # Create a new PDF document for annotations
            new_pdf = fitz.open()
            
            # Process each page
            for page_num in range(len(pdf_document)):
                original_page = pdf_document[page_num]
                
                # Create a new page with the same dimensions
                new_page = new_pdf.new_page(width=original_page.rect.width, height=original_page.rect.height)
                
                # Copy the original page content
                new_page.show_pdf_page(original_page.rect, pdf_document, page_num)
                
                # Add annotations based on explanations
                self._add_page_annotations(new_page, explanations, page_num)
            
            # Add a summary page with legend
            self._add_summary_page(new_pdf, explanations)
            
            # Save the annotated PDF to bytes
            pdf_bytes = new_pdf.write()
            
            # Close documents
            pdf_document.close()
            new_pdf.close()
            
            return pdf_bytes
            
        except Exception as e:
            st.error(f"Error creating annotated PDF: {e}")
            return None
    
    def _add_summary_page(self, pdf_document, explanations: List[PhraseExplanation]):
        """Add a summary page with legend and analysis"""
        
        # Create a new page for summary
        page = pdf_document.new_page(width=595, height=842)  # A4 size
        
        # Add title
        title_text = "Resume AI Analysis Summary"
        title_rect = fitz.Rect(50, 50, 545, 100)
        page.insert_text((50, 80), title_text, fontsize=24, color=(0.2, 0.2, 0.8))
        
        # Add legend
        legend_y = 120
        page.insert_text((50, legend_y), "Annotation Legend:", fontsize=16, color=(0, 0, 0))
        legend_y += 30
        
        # Green highlights
        page.insert_text((50, legend_y), "🟢 Green highlights = Strong positive match for the job", fontsize=12, color=(0.2, 0.8, 0.2))
        legend_y += 20
        
        # Yellow highlights
        page.insert_text((50, legend_y), "🟡 Yellow highlights = Moderate/good match", fontsize=12, color=(1.0, 0.8, 0.0))
        legend_y += 20
        
        # Red highlights
        page.insert_text((50, legend_y), "🔴 Red highlights = Areas that need improvement", fontsize=12, color=(0.8, 0.2, 0.2))
        legend_y += 30
        
        # Add statistics
        positive_count = len([exp for exp in explanations if exp.weight >= 5])
        neutral_count = len([exp for exp in explanations if 0 <= exp.weight < 5])
        negative_count = len([exp for exp in explanations if exp.weight < 0])
        
        page.insert_text((50, legend_y), "Analysis Statistics:", fontsize=16, color=(0, 0, 0))
        legend_y += 30
        
        page.insert_text((50, legend_y), f"Strong Matches: {positive_count} 🟢", fontsize=12, color=(0.2, 0.8, 0.2))
        legend_y += 20
        
        page.insert_text((50, legend_y), f"Moderate Matches: {neutral_count} 🟡", fontsize=12, color=(1.0, 0.8, 0.0))
        legend_y += 20
        
        page.insert_text((50, legend_y), f"Needs Improvement: {negative_count} 🔴", fontsize=12, color=(0.8, 0.2, 0.2))
        legend_y += 30
        
        # Add detailed explanations
        page.insert_text((50, legend_y), "Detailed Analysis:", fontsize=16, color=(0, 0, 0))
        legend_y += 30
        
        # Group explanations by weight
        positive_explanations = [exp for exp in explanations if exp.weight >= 5]
        neutral_explanations = [exp for exp in explanations if 0 <= exp.weight < 5]
        negative_explanations = [exp for exp in explanations if exp.weight < 0]
        
        # Add positive explanations
        if positive_explanations:
            page.insert_text((50, legend_y), "Strong Matches:", fontsize=14, color=(0.2, 0.8, 0.2))
            legend_y += 20
            
            for exp in positive_explanations[:5]:  # Show top 5
                text = f"• {exp.phrase} (+{exp.weight}) - {exp.justification[:60]}..."
                page.insert_text((70, legend_y), text, fontsize=10, color=(0, 0, 0))
                legend_y += 15
        
        # Add neutral explanations
        if neutral_explanations:
            page.insert_text((50, legend_y), "Moderate Matches:", fontsize=14, color=(1.0, 0.8, 0.0))
            legend_y += 20
            
            for exp in neutral_explanations[:3]:  # Show top 3
                text = f"• {exp.phrase} ({exp.weight:+d}) - {exp.justification[:60]}..."
                page.insert_text((70, legend_y), text, fontsize=10, color=(0, 0, 0))
                legend_y += 15
        
        # Add negative explanations
        if negative_explanations:
            page.insert_text((50, legend_y), "Areas for Improvement:", fontsize=14, color=(0.8, 0.2, 0.2))
            legend_y += 20
            
            for exp in negative_explanations[:3]:  # Show top 3
                text = f"• {exp.phrase} ({exp.weight:+d}) - {exp.justification[:60]}..."
                page.insert_text((70, legend_y), text, fontsize=10, color=(0, 0, 0))
                legend_y += 15
        
        # Add footer
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Resume AI Matcher Pro"
        page.insert_text((50, 800), footer_text, fontsize=10, color=(0.5, 0.5, 0.5))
    
    def _add_page_annotations(self, page, explanations: List[PhraseExplanation], page_num: int):
        """Add annotations to a specific page"""
        
        # Get page text and positions
        text_dict = page.get_text("dict")
        
        # Group explanations by weight for better organization
        positive_explanations = [exp for exp in explanations if exp.weight >= 5]
        neutral_explanations = [exp for exp in explanations if 0 <= exp.weight < 5]
        negative_explanations = [exp for exp in explanations if exp.weight < 0]
        
        # Add positive annotations (green highlights)
        self._add_highlight_annotations(page, positive_explanations, text_dict, (0.2, 0.8, 0.2, 0.3))  # Green with transparency
        
        # Add neutral annotations (yellow highlights)
        self._add_highlight_annotations(page, neutral_explanations, text_dict, (1.0, 1.0, 0.0, 0.3))  # Yellow with transparency
        
        # Add negative annotations (red highlights)
        self._add_highlight_annotations(page, negative_explanations, text_dict, (0.8, 0.2, 0.2, 0.3))  # Red with transparency
        
        # Add bubble annotations with explanations
        self._add_bubble_annotations(page, explanations, page_num)
    
    def _find_text_positions(self, page, target_phrase: str) -> List[tuple]:
        """Find all positions of a phrase in the page with improved matching"""
        found_positions = []
        target_phrase_lower = target_phrase.lower().strip()
        
        # Get page text with detailed information
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].lower()
                        
                        # Multiple matching strategies
                        if (target_phrase_lower in text or 
                            any(word in text for word in target_phrase_lower.split()) or
                            self._fuzzy_match(target_phrase_lower, text)):
                            
                            bbox = fitz.Rect(span["bbox"])
                            found_positions.append((bbox, span["text"], span.get("font", "")))
        
        return found_positions
    
    def _fuzzy_match(self, target: str, text: str) -> bool:
        """Simple fuzzy matching for text detection"""
        target_words = target.split()
        text_words = text.split()
        
        # Check if most target words are in the text
        matches = sum(1 for word in target_words if any(word in text_word for text_word in text_words))
        return matches >= max(1, len(target_words) * 0.7)  # 70% match threshold
    
    def _add_highlight_annotations(self, page, explanations: List[PhraseExplanation], text_dict: Dict, color: tuple):
        """Add highlight annotations to the page with improved text detection"""
        
        for explanation in explanations:
            phrase = explanation.phrase.strip()
            
            # Find all positions of this phrase
            found_positions = self._find_text_positions(page, phrase)
            
            # Add highlights for all found positions
            for bbox, original_text, font_info in found_positions:
                # Create highlight annotation
                highlight = page.add_highlight_annot(bbox)
                highlight.set_colors(stroke=color)
                highlight.set_opacity(0.6)
                
                # Add a text annotation with the explanation
                self._add_text_annotation(page, bbox, explanation, original_text)
                
                # Add a small indicator for the weight
                self._add_weight_indicator(page, bbox, explanation.weight)
    
    def _add_weight_indicator(self, page, bbox, weight: int):
        """Add a small weight indicator near the highlight"""
        
        # Determine indicator color based on weight
        if weight >= 5:
            color = (0.2, 0.8, 0.2)  # Green
            symbol = "🟢"
        elif weight >= 0:
            color = (1.0, 0.8, 0.0)  # Yellow
            symbol = "🟡"
        else:
            color = (0.8, 0.2, 0.2)  # Red
            symbol = "🔴"
        
        # Position indicator near the highlight
        indicator_pos = (bbox.x1 + 2, bbox.y0 - 15)
        
        # Add small text annotation as indicator
        indicator_annot = page.add_text_annot(indicator_pos, symbol)
        indicator_annot.set_colors(stroke=color)
        indicator_annot.set_opacity(0.8)
        indicator_annot.set_fontsize(10)
    
    def _add_text_annotation(self, page, bbox, explanation: PhraseExplanation, original_text: str = ""):
        """Add a text annotation with the explanation"""
        
        # Determine annotation color based on weight
        if explanation.weight >= 5:
            color = (0.2, 0.8, 0.2)  # Green
            icon = "✅"
        elif explanation.weight >= 0:
            color = (1.0, 0.8, 0.0)  # Yellow
            icon = "⚠️"
        else:
            color = (0.8, 0.2, 0.2)  # Red
            icon = "❌"
        
        # Create shorter annotation text for better display
        short_phrase = explanation.phrase[:30] + "..." if len(explanation.phrase) > 30 else explanation.phrase
        annotation_text = f"{icon} {short_phrase} ({explanation.weight:+d})"
        
        # Position the annotation near the highlighted text
        annot_bbox = fitz.Rect(bbox.x1 + 5, bbox.y0 - 25, bbox.x1 + 180, bbox.y0)
        
        # Add text annotation
        text_annot = page.add_text_annot(annot_bbox.tl, annotation_text)
        text_annot.set_colors(stroke=color)
        text_annot.set_opacity(0.9)
        text_annot.set_fontsize(8)
        
        # Add detailed explanation as a separate annotation
        detail_text = explanation.justification[:100] + "..." if len(explanation.justification) > 100 else explanation.justification
        detail_bbox = fitz.Rect(bbox.x1 + 5, bbox.y1 + 5, bbox.x1 + 250, bbox.y1 + 50)
        detail_annot = page.add_text_annot(detail_bbox.tl, detail_text)
        detail_annot.set_colors(stroke=(0, 0, 0))  # Black text
        detail_annot.set_opacity(0.8)
        detail_annot.set_fontsize(7)
    
    def _add_bubble_annotations(self, page, explanations: List[PhraseExplanation], page_num: int):
        """Add bubble-style annotations to the page with improved positioning"""
        
        # Get page dimensions
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Calculate strategic positions based on page size
        margin = 50
        positions = [
            (margin, margin),  # Top left
            (page_width/2 - 75, margin),  # Top center
            (page_width - 200, margin),  # Top right
            (margin, page_height/2 - 20),  # Middle left
            (page_width/2 - 75, page_height/2 - 20),  # Middle center
            (page_width - 200, page_height/2 - 20),  # Middle right
            (margin, page_height - 100),  # Bottom left
            (page_width/2 - 75, page_height - 100),  # Bottom center
            (page_width - 200, page_height - 100),  # Bottom right
        ]
        
        # Add bubble annotations for top explanations
        top_explanations = sorted(explanations, key=lambda x: abs(x.weight), reverse=True)[:len(positions)]
        
        for i, explanation in enumerate(top_explanations):
            if i < len(positions):
                x, y = positions[i]
                
                # Determine bubble color based on weight
                if explanation.weight >= 5:
                    fill_color = (0.2, 0.8, 0.2)  # Green
                    stroke_color = (0.1, 0.6, 0.1)  # Darker green
                    icon = "🟢"
                elif explanation.weight >= 0:
                    fill_color = (1.0, 0.8, 0.0)  # Yellow
                    stroke_color = (0.8, 0.6, 0.0)  # Darker yellow
                    icon = "🟡"
                else:
                    fill_color = (0.8, 0.2, 0.2)  # Red
                    stroke_color = (0.6, 0.1, 0.1)  # Darker red
                    icon = "🔴"
                
                # Create bubble annotation with rounded corners
                bubble_rect = fitz.Rect(x, y, x + 150, y + 40)
                
                # Add the bubble as a rectangle annotation with rounded corners
                bubble_annot = page.add_rect_annot(bubble_rect)
                bubble_annot.set_colors(stroke=stroke_color, fill=fill_color)
                bubble_annot.set_opacity(0.9)
                
                # Add text inside the bubble
                bubble_text = f"{icon} {explanation.phrase[:15]}... ({explanation.weight:+d})"
                text_annot = page.add_text_annot((x + 5, y + 12), bubble_text)
                text_annot.set_colors(stroke=(1, 1, 1))  # White text
                text_annot.set_fontsize(8)
                
                # Add detailed explanation as a popup below the bubble
                detail_text = explanation.justification[:80] + "..." if len(explanation.justification) > 80 else explanation.justification
                detail_rect = fitz.Rect(x, y + 45, x + 250, y + 120)
                detail_annot = page.add_text_annot((x, y + 50), detail_text)
                detail_annot.set_colors(stroke=(0, 0, 0))  # Black text
                detail_annot.set_fontsize(7)
                detail_annot.set_opacity(0.8) 
    
    def create_highlighted_pdf_display(self, resume_data: Dict, explanations: List[PhraseExplanation], uploaded_file_bytes=None) -> None:
        """Display the original PDF with enhanced highlighting and create downloadable annotated PDF"""
        import streamlit as st
        
        st.markdown("### 📄 Resume with AI Annotations")
        st.markdown("*Green highlights show strong matches, yellow shows moderate matches, red shows areas for improvement*")
        
        if uploaded_file_bytes is not None:
            # Create annotated PDF
            annotated_pdf_bytes = self.create_annotated_pdf(uploaded_file_bytes, explanations)
            
            if annotated_pdf_bytes:
                # Display the annotated PDF
                st.markdown("#### 🎯 **Annotated Resume PDF**")
                st.markdown("*This PDF contains actual annotations and highlighting directly on the document*")
                
                # Convert to base64 for display
                pdf_base64 = base64.b64encode(annotated_pdf_bytes).decode()
                
                # Display PDF with download option
                st.markdown(f"""
                <div style="margin: 20px 0;">
                    <iframe src="data:application/pdf;base64,{pdf_base64}" 
                            width="100%" height="600px" style="border: 2px solid #3498db; border-radius: 10px;">
                    </iframe>
                </div>
                """, unsafe_allow_html=True)
                
                # Download button for annotated PDF
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"annotated_resume_{timestamp}.pdf"
                
                st.download_button(
                    label="📥 Download Annotated PDF",
                    data=annotated_pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                    help="Download the PDF with AI annotations and highlighting"
                )
                
                # Show annotation legend
                st.markdown("---")
                st.markdown("""
                **📋 Annotation Legend:**
                - 🟢 **Green highlights** = Strong positive match for the job
                - 🟡 **Yellow highlights** = Moderate/good match
                - 🔴 **Red highlights** = Areas that need improvement
                - **Bubble annotations** = Detailed AI explanations
                - **Text annotations** = Specific feedback for each highlighted section
                """)
                
                # Display summary statistics
                positive_count = len([exp for exp in explanations if exp.weight >= 5])
                neutral_count = len([exp for exp in explanations if 0 <= exp.weight < 5])
                negative_count = len([exp for exp in explanations if exp.weight < 0])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Strong Matches", positive_count, "🟢", delta_color="normal")
                with col2:
                    st.metric("Moderate Matches", neutral_count, "🟡", delta_color="normal")
                with col3:
                    st.metric("Needs Improvement", negative_count, "🔴", delta_color="inverse")
                
            else:
                st.error("❌ Failed to create annotated PDF")
                # Fallback to original display
                self.display_original_pdf_with_annotations(uploaded_file_bytes, explanations)
        else:
            st.warning("No original file available. Showing text analysis.")
            self.display_text_with_annotations(explanations) 
    
 