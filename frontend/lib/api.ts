import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ResumeData {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  experience: Array<{
    role: string;
    company: string;
    duration: string;
    description: string;
  }>;
  education: Array<{
    degree: string;
    institution: string;
    year: string;
    gpa: string;
  }>;
  projects: string[];
  certifications: string[];
  achievements: string[];
}

export interface JobDescriptionRequest {
  role: string;
  keywords: string;
  industry: string;
}

export interface JobDescriptionResponse {
  job_description: string;
  generated: boolean;
}

export interface MatchRequest {
  resume_data: ResumeData;
  job_description: string;
  analysis_type: 'standard' | 'explainable';
}

export interface PhraseExplanation {
  phrase: string;
  weight: number; // -10 to +10
  justification: string;
  category: string; // "skill", "experience", "education", "achievement", etc.
}

export interface ExplainableMatchResponse {
  match_score: number;
  explanations: PhraseExplanation[];
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

export interface MatchResponse {
  match_score: number;
  reasoning: {
    skills_match: string;
    experience_alignment: string;
    project_relevance: string;
    bonus_factors: string;
  };
  strengths: string[];
  missing: string[];
  skill_gap_suggestions: string[];
  learning_resources: Array<{
    topic: string;
    link: string;
  }>;
  resume_enhancer: Array<{
    current_line: string;
    suggestion: string;
  }>;
}

export interface EnhancedResumeResponse {
  enhanced_bullet_points: string[];
  power_verbs: string[];
  quantified_achievements: string[];
  skill_improvements: string[];
  formatting_suggestions: string[];
}

export const resumeAPI = {
  // Upload and parse resume
  uploadResume: async (file: File): Promise<{
    success: boolean;
    resume_data: ResumeData;
    file_base64: string;
    file_name: string;
    file_type: string;
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Generate job description
  generateJobDescription: async (request: JobDescriptionRequest): Promise<JobDescriptionResponse> => {
    const response = await api.post('/generate-job-description', request);
    return response.data;
  },

  // Match resume to job
  matchResume: async (request: MatchRequest): Promise<MatchResponse | ExplainableMatchResponse> => {
    const response = await api.post('/match-resume', request);
    return response.data;
  },

  // Enhance resume
  enhanceResume: async (request: MatchRequest): Promise<EnhancedResumeResponse> => {
    const response = await api.post('/enhance-resume', request);
    return response.data;
  },

  // Create annotated PDF
  createAnnotatedPDF: async (file: File, explanations: PhraseExplanation[]): Promise<{ annotated_pdf_base64: string; file_name: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('explanations', JSON.stringify(explanations));
    
    const response = await api.post('/create-annotated-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
};

export default api; 