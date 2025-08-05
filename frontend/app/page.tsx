'use client';

import React, { useState, useCallback } from 'react';
import { Brain, Zap, Target, TrendingUp, Eye, Star } from 'lucide-react';
import { ResumeData, MatchResponse, EnhancedResumeResponse, ExplainableMatchResponse } from '../lib/api';
import ResumeUpload from '../components/ResumeUpload';
import JobDescriptionInput from '../components/JobDescriptionInput';
import AnalysisResults from '../components/AnalysisResults';
import { ExplainableAnalysis } from '../components/ExplainableAnalysis';
import { InteractiveResumeScanner } from '../components/InteractiveResumeScanner';
import { LivePDFScanner } from '../components/LivePDFScanner';
import { AnimatedPDFScanner } from '../components/AnimatedPDFScanner';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

export default function Home() {
  const [currentStep, setCurrentStep] = useState(1);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');
  const [matchResults, setMatchResults] = useState<MatchResponse | null>(null);
  const [explainableResults, setExplainableResults] = useState<ExplainableMatchResponse | null>(null);
  const [enhancedResume, setEnhancedResume] = useState<EnhancedResumeResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  // Both features are mandatory - no toggles needed
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleResumeParsed = useCallback((data: ResumeData, fileBase64: string, fileName: string, file?: File) => {
    setResumeData(data);
    if (file) setUploadedFile(file);
    setCurrentStep(2);
    setError(null);
  }, []);

  const handleJobDescriptionSet = useCallback((description: string) => {
    setJobDescription(description);
    setCurrentStep(3);
    setError(null);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!resumeData || !jobDescription) {
      setError('Please complete all steps before analyzing');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Import the API functions dynamically to avoid SSR issues
      const { resumeAPI } = await import('../lib/api');

      // Always use explainable analysis with animated PDF scanning
      const matchRequest = {
        resume_data: resumeData,
        job_description: jobDescription,
        analysis_type: 'explainable' as const,
      };

      const matchResult = await resumeAPI.matchResume(matchRequest);
      setExplainableResults(matchResult as ExplainableMatchResponse);
      setMatchResults(null);

      // Perform resume enhancement
      const enhancedResult = await resumeAPI.enhanceResume(matchRequest);
      setEnhancedResume(enhancedResult);

      setCurrentStep(4);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze resume');
    } finally {
      setIsAnalyzing(false);
    }
  }, [resumeData, jobDescription]);

  const resetAnalysis = useCallback(() => {
    setCurrentStep(1);
    setResumeData(null);
    setJobDescription('');
    setMatchResults(null);
    setExplainableResults(null);
    setEnhancedResume(null);
    // No toggles to reset - both features are mandatory
    setError(null);
    setUploadedFile(null);
  }, []);

  const steps = [
    { id: 1, title: 'Upload Resume', description: 'Upload and parse your resume' },
    { id: 2, title: 'Job Description', description: 'Add or generate job description' },
    { id: 3, title: 'AI Analysis', description: 'Run AI-powered analysis' },
    { id: 4, title: 'Results', description: 'View detailed analysis results' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Resume AI Matcher Pro</h1>
                <p className="text-sm text-gray-600">Advanced AI-powered resume analysis</p>
              </div>
            </div>
            
            {currentStep > 1 && (
              <Button
                onClick={resetAnalysis}
                variant="secondary"
                size="sm"
              >
                Start Over
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                    currentStep >= step.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step.id}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">{step.title}</p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`w-16 h-0.5 mx-4 ${
                      currentStep > step.id ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Welcome to Resume AI Matcher Pro
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Upload your resume and get AI-powered analysis to match it with job descriptions. 
                  Our advanced algorithms will provide detailed insights and suggestions for improvement.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Card className="text-center">
                  <Brain className="w-12 h-12 text-primary-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
                  <p className="text-sm text-gray-600">
                    Advanced machine learning algorithms analyze your resume against job requirements
                  </p>
                </Card>
                <Card className="text-center">
                  <Target className="w-12 h-12 text-success-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Matching</h3>
                  <p className="text-sm text-gray-600">
                    Get detailed match scores and specific areas for improvement
                  </p>
                </Card>
                <Card className="text-center">
                  <TrendingUp className="w-12 h-12 text-warning-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Enhancement Suggestions</h3>
                  <p className="text-sm text-gray-600">
                    Receive actionable advice to improve your resume and career prospects
                  </p>
                </Card>
              </div>

              <ResumeUpload onResumeParsed={handleResumeParsed} />
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Step 2: Job Description</h2>
                <p className="text-gray-600">
                  Add a job description to compare against your resume
                </p>
              </div>

              <JobDescriptionInput onJobDescriptionSet={handleJobDescriptionSet} />
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Step 3: AI Analysis</h2>
                <p className="text-gray-600">
                  Ready to analyze your resume against the job description
                </p>
              </div>

              <Card>
                <div className="space-y-4">
                  <div className="flex items-center justify-center space-x-2 mb-4">
                    <Zap className="w-6 h-6 text-primary-600" />
                    <h3 className="text-lg font-semibold text-gray-900">Ready to Analyze</h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Resume Data</h4>
                      <p className="text-sm text-blue-700">
                        {resumeData?.name || 'N/A'} • {resumeData?.skills.length || 0} skills detected
                      </p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="font-medium text-green-900 mb-2">Job Description</h4>
                      <p className="text-sm text-green-700">
                        {jobDescription.length > 100 
                          ? `${jobDescription.substring(0, 100)}...` 
                          : jobDescription}
                      </p>
                    </div>
                  </div>

                  {/* Mandatory Features Description */}
                  <div className="space-y-4">
                    <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                      <div className="flex items-center space-x-3 mb-3">
                        <Brain className="w-6 h-6 text-purple-600" />
                        <Star className="w-6 h-6 text-indigo-600" />
                        <h4 className="font-medium text-purple-900">Advanced AI Analysis</h4>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-purple-700">
                          <strong>🧠 Explainable AI:</strong> Get detailed explanations for each phrase that impacts your match score
                        </p>
                        <p className="text-sm text-indigo-700">
                          <strong>✨ Animated PDF Scanner:</strong> Beautiful circular bubble scanning with smooth animations and visual effects
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={handleAnalyze}
                    loading={isAnalyzing}
                    className="w-full"
                    size="lg"
                  >
                    <Brain className="w-5 h-5 mr-2" />
                    Start AI Analysis
                  </Button>
                </div>
              </Card>

              {error && (
                <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg">
                  <p className="text-danger-700">{error}</p>
                </div>
              )}
            </div>
          )}

          {currentStep === 4 && (matchResults || explainableResults) && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Complete!</h2>
                <p className="text-gray-600">
                  Your resume has been analyzed. Review the results below.
                </p>
              </div>

              {explainableResults ? (
                <AnimatedPDFScanner
                  resumeText={resumeData ? JSON.stringify(resumeData, null, 2) : ''}
                  explanations={explainableResults.explanations}
                  matchScore={explainableResults.match_score}
                  summary={explainableResults.summary}
                  strengths={explainableResults.strengths}
                  weaknesses={explainableResults.weaknesses}
                  suggestions={explainableResults.suggestions}
                  uploadedFile={uploadedFile || undefined}
                  resumeData={resumeData}
                  onComplete={() => {
                    // Animation complete - show the full analysis
                  }}
                />
              ) : (
                <AnalysisResults 
                  matchResults={matchResults!} 
                  enhancedResume={enhancedResume || undefined}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 