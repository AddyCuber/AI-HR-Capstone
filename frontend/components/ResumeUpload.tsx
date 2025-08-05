import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { resumeAPI, ResumeData } from '../lib/api';
import Button from './ui/Button';
import Card from './ui/Card';

interface ResumeUploadProps {
  onResumeParsed: (resumeData: ResumeData, fileBase64: string, fileName: string, file?: File) => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ onResumeParsed }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setError(null);
    }
  }, []);

  const handleUpload = useCallback(async () => {
    if (!uploadedFile) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const result = await resumeAPI.uploadResume(uploadedFile);
      
      if (result.success) {
        onResumeParsed(result.resume_data, result.file_base64, result.file_name, uploadedFile);
      } else {
        setError('Failed to parse resume');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload resume');
    } finally {
      setIsUploading(false);
    }
  }, [uploadedFile, onResumeParsed]);

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setUploadedFile(file);
      setError(null);
    }
  }, []);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  }, []);

  return (
    <Card title="📄 Resume Upload" subtitle="Upload your resume to get started">
      <div className="space-y-4">
        {/* File Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            uploadedFile
              ? 'border-success-300 bg-success-50'
              : 'border-gray-300 hover:border-primary-400 hover:bg-primary-50'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {uploadedFile ? (
            <div className="flex items-center justify-center space-x-2">
              <CheckCircle className="w-6 h-6 text-success-600" />
              <span className="text-success-700 font-medium">
                {uploadedFile.name} selected
              </span>
            </div>
          ) : (
            <div className="space-y-2">
              <Upload className="w-12 h-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Drop your resume here
                </p>
                <p className="text-sm text-gray-500">
                  or click to browse files
                </p>
              </div>
              <p className="text-xs text-gray-400">
                Supports PDF, DOCX, and TXT files (max 10MB)
              </p>
            </div>
          )}
          
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="hidden"
            id="resume-upload"
          />
          <label
            htmlFor="resume-upload"
            className="btn-primary inline-block mt-4 cursor-pointer"
          >
            Choose File
          </label>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-center space-x-2 p-3 bg-danger-50 border border-danger-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-danger-600" />
            <span className="text-danger-700 text-sm">{error}</span>
          </div>
        )}

        {/* Upload Button */}
        {uploadedFile && (
          <div className="flex justify-center">
            <Button
              onClick={handleUpload}
              loading={isUploading}
              disabled={!uploadedFile}
              className="w-full"
            >
              <FileText className="w-4 h-4 mr-2" />
              Parse Resume
            </Button>
          </div>
        )}

        {/* Supported Formats */}
        <div className="text-xs text-gray-500 text-center">
          <p>Supported formats: PDF, DOCX, TXT</p>
          <p>Maximum file size: 10MB</p>
        </div>
      </div>
    </Card>
  );
};

export default ResumeUpload; 