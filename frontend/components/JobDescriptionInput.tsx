import React, { useState, useCallback } from 'react';
import { Briefcase, Sparkles, FileText, AlertCircle } from 'lucide-react';
import { resumeAPI, JobDescriptionRequest } from '../lib/api';
import Button from './ui/Button';
import Card from './ui/Card';

interface JobDescriptionInputProps {
  onJobDescriptionSet: (jobDescription: string) => void;
}

const JobDescriptionInput: React.FC<JobDescriptionInputProps> = ({ onJobDescriptionSet }) => {
  const [inputMethod, setInputMethod] = useState<'generate' | 'upload' | 'manual'>('generate');
  const [role, setRole] = useState('');
  const [keywords, setKeywords] = useState('');
  const [industry, setIndustry] = useState('');
  const [manualJobDescription, setManualJobDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleGenerateJobDescription = useCallback(async () => {
    if (!role || !keywords) {
      setError('Please provide both role and keywords');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request: JobDescriptionRequest = {
        role,
        keywords,
        industry,
      };

      const result = await resumeAPI.generateJobDescription(request);
      onJobDescriptionSet(result.job_description);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate job description');
    } finally {
      setIsGenerating(false);
    }
  }, [role, keywords, industry, onJobDescriptionSet]);

  const handleManualSubmit = useCallback(() => {
    if (!manualJobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }
    setError(null);
    onJobDescriptionSet(manualJobDescription);
  }, [manualJobDescription, onJobDescriptionSet]);

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setError(null);
      
      // Read file content
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setManualJobDescription(content);
        onJobDescriptionSet(content);
      };
      reader.readAsText(file);
    }
  }, [onJobDescriptionSet]);

  return (
    <Card title="💼 Job Description" subtitle="Add or generate a job description">
      <div className="space-y-6">
        {/* Input Method Selection */}
        <div className="flex space-x-2">
          <button
            onClick={() => setInputMethod('generate')}
            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
              inputMethod === 'generate'
                ? 'bg-primary-100 text-primary-700 border-2 border-primary-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Sparkles className="w-4 h-4 mr-2 inline" />
            Generate with AI
          </button>
          <button
            onClick={() => setInputMethod('upload')}
            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
              inputMethod === 'upload'
                ? 'bg-primary-100 text-primary-700 border-2 border-primary-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <FileText className="w-4 h-4 mr-2 inline" />
            Upload File
          </button>
          <button
            onClick={() => setInputMethod('manual')}
            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
              inputMethod === 'manual'
                ? 'bg-primary-100 text-primary-700 border-2 border-primary-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Briefcase className="w-4 h-4 mr-2 inline" />
            Type Manually
          </button>
        </div>

        {/* Generate with AI */}
        {inputMethod === 'generate' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Role *
                </label>
                <input
                  type="text"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  placeholder="e.g., Software Engineer"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry
                </label>
                <input
                  type="text"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  placeholder="e.g., Technology"
                  className="input-field"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Key Requirements *
              </label>
              <textarea
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g., Python, React, AWS, 3+ years experience"
                className="input-field"
                rows={3}
              />
            </div>
            <Button
              onClick={handleGenerateJobDescription}
              loading={isGenerating}
              disabled={!role || !keywords}
              className="w-full"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Generate Job Description
            </Button>
          </div>
        )}

        {/* Upload File */}
        {inputMethod === 'upload' && (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm text-gray-600 mb-4">
                Upload a job description file (PDF, TXT, DOCX)
              </p>
              <input
                type="file"
                accept=".pdf,.txt,.docx"
                onChange={handleFileUpload}
                className="hidden"
                id="jd-upload"
              />
              <label
                htmlFor="jd-upload"
                className="btn-primary inline-block cursor-pointer"
              >
                Choose File
              </label>
            </div>
          </div>
        )}

        {/* Manual Input */}
        {inputMethod === 'manual' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Description
              </label>
              <textarea
                value={manualJobDescription}
                onChange={(e) => setManualJobDescription(e.target.value)}
                placeholder="Paste or type the job description here..."
                className="input-field"
                rows={8}
              />
            </div>
            <Button
              onClick={handleManualSubmit}
              disabled={!manualJobDescription.trim()}
              className="w-full"
            >
              <Briefcase className="w-4 h-4 mr-2" />
              Use This Job Description
            </Button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="flex items-center space-x-2 p-3 bg-danger-50 border border-danger-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-danger-600" />
            <span className="text-danger-700 text-sm">{error}</span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default JobDescriptionInput; 