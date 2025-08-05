"""
Few-Shot Learning Examples for Resume AI Matcher
Comprehensive examples for training AI models to perform better matching
"""

FEW_SHOT_EXAMPLES = {
    "full_stack_developer": {
        "job_description": {
            "role": "Full-Stack Developer",
            "company": "TechNova Solutions",
            "responsibilities": [
                "Build scalable web applications using React and Node.js",
                "Integrate backend services and APIs",
                "Work with MongoDB for data storage",
                "Follow CI/CD best practices (Git, GitHub Actions)",
                "Collaborate in Agile teams"
            ],
            "requirements": [
                "1–2 years of experience in web development",
                "Strong understanding of JavaScript, React, Node.js",
                "Familiarity with MongoDB, REST APIs, and Git",
                "Bonus: Experience with Docker, Jenkins, or unit testing"
            ]
        },
        "resume_data": {
            "name": "Aditya Ray",
            "email": "aditya.ray036@nmims.in",
            "education": [
                {
                    "degree": "B.Tech in AI & Data Science",
                    "institution": "NMIMS Navi Mumbai",
                    "year": 2025
                }
            ],
            "skills": ["JavaScript", "React", "Node.js", "Express", "MySQL", "Git", "AWS (basic)", "Python"],
            "experience": [
                {
                    "company": "ByteForge Labs",
                    "role": "Web Developer Intern",
                    "duration": "3 months",
                    "description": "Built internal dashboards using React and integrated them with Node.js APIs."
                },
                {
                    "company": "To Be Deployed (Startup)",
                    "role": "Founder & Backend Engineer",
                    "duration": "Ongoing",
                    "description": "Designed end-to-end API systems using Node.js, worked on resume parsing using Python."
                }
            ],
            "projects": [
                {
                    "title": "AI Resume Matcher",
                    "tools": ["React", "FastAPI", "HuggingFace", "LangChain"],
                    "summary": "Built a smart resume matching tool that evaluates candidates using LLMs."
                },
                {
                    "title": "E-Commerce Clone",
                    "tools": ["React", "Node.js", "MongoDB"],
                    "summary": "Developed a full-stack e-commerce web app with product filtering and user authentication."
                }
            ]
        },
        "expected_output": {
            "match_score": 87,
            "reasoning": {
                "skills_match": "Excellent overlap in JavaScript, React, Node.js, and Git. MongoDB experience demonstrated in project, though not in work experience.",
                "experience_alignment": "Internship and startup work both show hands-on experience with full-stack tools. Although formal experience is ~3–6 months, startup role adds depth.",
                "project_relevance": "The E-Commerce clone and resume matcher are directly aligned with the responsibilities. They show initiative and the ability to build end-to-end systems.",
                "bonus_factors": "Mentions AWS basics, familiarity with Python and FastAPI. Some knowledge of deployment tools is evident, though no mention of Docker or Jenkins."
            },
            "strengths": [
                "Strong React and Node.js experience from both internship and projects.",
                "Good understanding of REST APIs, Git, and Agile-style development.",
                "Full-stack implementation proven via projects."
            ],
            "missing": [
                "No mention of Docker, Jenkins, or unit testing.",
                "MongoDB is shown only in project, not in professional context."
            ],
            "resume_enhancer": [
                {
                    "current_line": "Developed a full-stack e-commerce web app...",
                    "suggestion": "Built and deployed a responsive full-stack e-commerce web app using React, Node.js, and MongoDB, with features like user auth and product search — deployed on Render."
                },
                {
                    "current_line": "Built internal dashboards using React...",
                    "suggestion": "Built interactive dashboards in React and integrated them with backend APIs in Node.js, improving internal task visibility by 40%."
                }
            ],
            "skill_gap_suggestions": [
                "Add mention of unit testing with Jest or Mocha, if done.",
                "Try Dockerizing one project and mention it under skills.",
                "Clarify MongoDB use in professional roles, if applicable."
            ],
            "learning_resources": [
                {"topic": "Docker Basics", "link": "https://docker-curriculum.com/"},
                {"topic": "Unit Testing in JavaScript", "link": "https://jestjs.io/docs/getting-started"}
            ]
        }
    },
    
    "data_scientist": {
        "job_description": {
            "role": "Data Scientist",
            "company": "DataCorp Analytics",
            "responsibilities": [
                "Develop machine learning models for predictive analytics",
                "Analyze large datasets using Python and SQL",
                "Create data visualizations and dashboards",
                "Collaborate with engineering teams to deploy models",
                "Present findings to stakeholders"
            ],
            "requirements": [
                "2+ years of experience in data science or analytics",
                "Strong Python programming skills (pandas, numpy, scikit-learn)",
                "Experience with SQL and data visualization tools",
                "Knowledge of machine learning algorithms",
                "Bonus: Experience with deep learning, cloud platforms, or MLOps"
            ]
        },
        "resume_data": {
            "name": "Sarah Chen",
            "email": "sarah.chen@email.com",
            "education": [
                {
                    "degree": "M.S. in Data Science",
                    "institution": "Stanford University",
                    "year": 2023
                }
            ],
            "skills": ["Python", "pandas", "numpy", "scikit-learn", "SQL", "Tableau", "TensorFlow", "AWS"],
            "experience": [
                {
                    "company": "Analytics Inc",
                    "role": "Data Analyst",
                    "duration": "2 years",
                    "description": "Built predictive models for customer churn using Python and scikit-learn."
                }
            ],
            "projects": [
                {
                    "title": "Customer Segmentation Model",
                    "tools": ["Python", "scikit-learn", "pandas"],
                    "summary": "Developed clustering model to segment customers based on purchasing behavior."
                }
            ]
        },
        "expected_output": {
            "match_score": 82,
            "reasoning": {
                "skills_match": "Strong Python skills with relevant libraries. Good SQL and visualization experience.",
                "experience_alignment": "2 years as Data Analyst shows relevant experience, though role title is slightly different.",
                "project_relevance": "Customer segmentation project directly relates to predictive analytics requirements.",
                "bonus_factors": "AWS experience is valuable. TensorFlow knowledge shows deep learning capability."
            },
            "strengths": [
                "Strong Python programming with relevant data science libraries.",
                "Relevant experience in predictive modeling.",
                "Good educational background in data science."
            ],
            "missing": [
                "Limited experience with deep learning frameworks in practice.",
                "No mention of MLOps or model deployment experience."
            ],
            "resume_enhancer": [
                {
                    "current_line": "Built predictive models for customer churn...",
                    "suggestion": "Developed and deployed customer churn prediction models using Python and scikit-learn, achieving 85% accuracy and reducing churn by 15%."
                }
            ],
            "skill_gap_suggestions": [
                "Highlight any model deployment experience.",
                "Add specific metrics and business impact to projects.",
                "Consider adding MLOps tools like MLflow or Kubeflow."
            ],
            "learning_resources": [
                {"topic": "MLOps Fundamentals", "link": "https://mlops.community/"},
                {"topic": "Model Deployment", "link": "https://www.tensorflow.org/tfx"}
            ]
        }
    },
    
    "devops_engineer": {
        "job_description": {
            "role": "DevOps Engineer",
            "company": "CloudTech Solutions",
            "responsibilities": [
                "Design and implement CI/CD pipelines",
                "Manage cloud infrastructure (AWS/Azure)",
                "Automate deployment processes",
                "Monitor system performance and reliability",
                "Implement security best practices"
            ],
            "requirements": [
                "3+ years of DevOps or infrastructure experience",
                "Experience with Docker, Kubernetes, and cloud platforms",
                "Knowledge of CI/CD tools (Jenkins, GitLab CI)",
                "Familiarity with monitoring tools (Prometheus, Grafana)",
                "Bonus: Experience with Terraform, Ansible, or security tools"
            ]
        },
        "resume_data": {
            "name": "Mike Johnson",
            "email": "mike.j@email.com",
            "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Python", "Bash", "Git"],
            "experience": [
                {
                    "company": "TechStart",
                    "role": "System Administrator",
                    "duration": "4 years",
                    "description": "Managed server infrastructure and implemented basic automation scripts."
                }
            ],
            "projects": [
                {
                    "title": "Infrastructure as Code",
                    "tools": ["Terraform", "AWS", "Docker"],
                    "summary": "Automated infrastructure provisioning using Terraform and Docker containers."
                }
            ]
        },
        "expected_output": {
            "match_score": 75,
            "reasoning": {
                "skills_match": "Good overlap in Docker, AWS, and basic DevOps tools. Missing some advanced CI/CD experience.",
                "experience_alignment": "System Administrator role provides relevant infrastructure experience, though not specifically DevOps.",
                "project_relevance": "Infrastructure as Code project shows modern DevOps practices.",
                "bonus_factors": "Python and Bash scripting skills are valuable for automation."
            },
            "strengths": [
                "Strong infrastructure management experience.",
                "Good knowledge of containerization and cloud platforms.",
                "Infrastructure as Code experience with Terraform."
            ],
            "missing": [
                "Limited CI/CD pipeline experience.",
                "No mention of monitoring tools or security practices."
            ],
            "resume_enhancer": [
                {
                    "current_line": "Managed server infrastructure...",
                    "suggestion": "Managed and automated server infrastructure supporting 100+ applications, reducing deployment time by 60% through scripting and containerization."
                }
            ],
            "skill_gap_suggestions": [
                "Add experience with CI/CD pipeline tools.",
                "Include monitoring and logging tools experience.",
                "Highlight any security implementation work."
            ],
            "learning_resources": [
                {"topic": "CI/CD Best Practices", "link": "https://jenkins.io/doc/"},
                {"topic": "Monitoring with Prometheus", "link": "https://prometheus.io/docs/"}
            ]
        }
    },
    
    "ai_ml_engineer_nlp": {
        "job_description": {
            "role": "AI/ML Engineer – NLP",
            "company": "DeepInsight AI",
            "responsibilities": [
                "Build and fine-tune NLP models using Transformers, spaCy, or OpenAI APIs",
                "Perform data preprocessing, annotation, and model evaluation",
                "Deploy models with FastAPI/Flask, and integrate with web applications",
                "Work with HuggingFace Transformers, LangChain, and LLMs for generative use-cases",
                "Collaborate with frontend/backend teams for model integration"
            ],
            "requirements": [
                "Proficiency in Python, NLP libraries, and model deployment",
                "Experience with LLMs, embeddings, vector stores (e.g., FAISS)",
                "Knowledge of prompt engineering and evaluation metrics",
                "Bonus: Familiarity with Whisper, WhisperX, or voice-based AI pipelines"
            ]
        },
        "resume_data": {
            "name": "Aditya Ray",
            "email": "aditya.ray036@nmims.in",
            "education": [
                {
                    "degree": "B.Tech in AI & Data Science",
                    "institution": "NMIMS Navi Mumbai",
                    "year": 2025
                }
            ],
            "skills": [
                "Python", "Transformers", "LangChain", "HuggingFace", "FastAPI",
                "WhisperX", "FAISS", "Modal", "LLM Prompt Engineering", "Streamlit"
            ],
            "experience": [
                {
                    "company": "To Be Deployed (Startup)",
                    "role": "AI/Backend Engineer",
                    "duration": "Jan 2024 – Present",
                    "description": "Built an AI-powered podcast clipper using WhisperX, Gemini, and LangChain; integrated vertical video generation with subtitles and speaker detection."
                },
                {
                    "company": "IEEE Club, NMIMS",
                    "role": "Technical Head",
                    "duration": "2023 – Present",
                    "description": "Led AI workshops and built GPT-based internal tools for summarization and content planning."
                }
            ],
            "projects": [
                {
                    "title": "Resume Matching Platform",
                    "tools": ["LangChain", "FAISS", "GPT-4", "FastAPI"],
                    "summary": "Built an AI tool that matches parsed resumes to JDs using vector search + LLM scoring logic."
                },
                {
                    "title": "AI Podcast Clipper",
                    "tools": ["WhisperX", "Modal", "Gemini", "S3"],
                    "summary": "Transcribes podcasts, detects speakers, extracts clips using LLMs, and overlays subtitles."
                }
            ]
        },
        "expected_output": {
            "match_score": 92,
            "reasoning": {
                "skills_match": "Direct overlap in Python, FastAPI, Transformers, LangChain, and HuggingFace usage. WhisperX and Gemini usage match bonus expectations.",
                "experience_alignment": "Hands-on experience with production-level AI pipelines. The podcast clipper project directly maps to audio-NLP processing. Resume matcher demonstrates domain familiarity.",
                "project_relevance": "Two major AI projects show understanding of model integration, vector search, and LLM alignment. Real-world deployment via FastAPI and Modal is a plus.",
                "bonus_factors": "Exposure to speaker detection (LR-ASD), subtitle overlaying, and clip segmentation adds advanced value. Shows initiative and ownership."
            },
            "strengths": [
                "Experience with LLM tools (LangChain, Gemini, OpenAI) and infrastructure (Modal, S3).",
                "Hands-on with WhisperX, matching bonus requirement precisely.",
                "Deployable, real-world AI systems with clear impact."
            ],
            "missing": [
                "No mention of classical NLP models (e.g., spaCy, traditional NER).",
                "Unclear if familiar with evaluation metrics like BLEU, ROUGE, F1 for NLP."
            ],
            "resume_enhancer": [
                {
                    "current_line": "Built an AI-powered podcast clipper...",
                    "suggestion": "Built and deployed an AI podcast clipper using WhisperX and Gemini, extracting high-engagement vertical clips with face tracking, speaker diarization, and real-time transcription."
                },
                {
                    "current_line": "Built an AI tool that matches parsed resumes...",
                    "suggestion": "Developed an LLM-powered resume matching engine using LangChain and FAISS, scoring candidates against job descriptions and providing personalized feedback."
                }
            ],
            "skill_gap_suggestions": [
                "Mention or demonstrate understanding of model evaluation (e.g., accuracy, F1, BLEU).",
                "Add traditional NLP libraries (spaCy/TF-IDF) to cover hybrid pipelines.",
                "Include any experience with dataset annotation or prompt tuning processes."
            ],
            "learning_resources": [
                {"topic": "NLP Evaluation Metrics", "link": "https://huggingface.co/metrics"},
                {"topic": "spaCy for NLP pipelines", "link": "https://course.spacy.io/"}
            ]
        }
    }
}

# Few-shot examples for specific parsing tasks
PARSING_EXAMPLES = {
    "name_extraction": [
        {
            "text": "John Smith\nSoftware Engineer\njohn.smith@email.com",
            "name": "John Smith"
        },
        {
            "text": "Sarah Johnson\nData Scientist\nsarah.j@company.com", 
            "name": "Sarah Johnson"
        },
        {
            "text": "Michael Chen\nProduct Manager\nmchen@tech.com",
            "name": "Michael Chen"
        },
        {
            "text": "Aditya Ray\nFull Stack Developer\naditya.ray036@nmims.in",
            "name": "Aditya Ray"
        }
    ],
    
    "skill_extraction": [
        {
            "text": "Skills: Python, JavaScript, React, AWS, Docker, Kubernetes, Git, SQL",
            "skills": ["Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes", "Git", "SQL"]
        },
        {
            "text": "Technologies: Java, Spring Boot, MySQL, Redis, Jenkins, Maven",
            "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Jenkins", "Maven"]
        },
        {
            "text": "Programming: C++, Python, Machine Learning, TensorFlow, PyTorch, pandas",
            "skills": ["C++", "Python", "Machine Learning", "TensorFlow", "PyTorch", "pandas"]
        },
        {
            "text": "Tools & Technologies: React, Node.js, Express, MongoDB, Git, AWS, Docker",
            "skills": ["React", "Node.js", "Express", "MongoDB", "Git", "AWS", "Docker"]
        }
    ],
    
    "experience_extraction": [
        {
            "text": "Software Engineer at Google (2020-2023)\n- Developed scalable web applications using React and Node.js\n- Led team of 5 developers",
            "experience": [
                {
                    "role": "Software Engineer",
                    "company": "Google", 
                    "duration": "2020-2023",
                    "description": "Developed scalable web applications using React and Node.js. Led team of 5 developers."
                }
            ]
        },
        {
            "text": "Data Scientist - Microsoft (2019-2022)\n- Built ML models for prediction\n- Improved accuracy by 25%",
            "experience": [
                {
                    "role": "Data Scientist",
                    "company": "Microsoft",
                    "duration": "2019-2022", 
                    "description": "Built ML models for prediction. Improved accuracy by 25%."
                }
            ]
        },
        {
            "text": "Web Developer Intern at ByteForge Labs (3 months)\n- Built internal dashboards using React\n- Integrated with Node.js APIs",
            "experience": [
                {
                    "role": "Web Developer Intern",
                    "company": "ByteForge Labs",
                    "duration": "3 months",
                    "description": "Built internal dashboards using React. Integrated with Node.js APIs."
                }
            ]
        }
    ],
    
    "education_extraction": [
        {
            "text": "B.Tech in AI & Data Science\nNMIMS Navi Mumbai\n2025",
            "education": [
                {
                    "degree": "B.Tech in AI & Data Science",
                    "institution": "NMIMS Navi Mumbai",
                    "year": "2025",
                    "gpa": ""
                }
            ]
        },
        {
            "text": "Master of Science in Computer Science\nStanford University\n2023\nGPA: 3.8/4.0",
            "education": [
                {
                    "degree": "Master of Science in Computer Science",
                    "institution": "Stanford University", 
                    "year": "2023",
                    "gpa": "3.8/4.0"
                }
            ]
        }
    ]
}

# Enhanced matching prompts using few-shot examples
MATCHING_PROMPTS = {
    "comprehensive_analysis": """
    Analyze the following resume against the job description using these examples as reference:
    
    {few_shot_examples}
    
    **Resume Data:**
    {resume_data}
    
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
    """,
    
    "enhancement_suggestions": """
    Based on these examples, provide resume enhancement suggestions:
    
    {enhancement_examples}
    
    **Resume Data:**
    {resume_data}
    
    **Job Description:**
    {job_description}
    
    Provide enhancement suggestions in JSON format:
    {{
        "enhanced_bullet_points": [
            "Action verb + technology + impact + metrics"
        ],
        "power_verbs": ["List of action verbs"],
        "quantified_achievements": ["Achievements with numbers"],
        "skill_improvements": ["Specific skill suggestions"],
        "formatting_suggestions": ["Formatting recommendations"]
    }}
    """
} 