'use client';

import React, { useState } from 'react';
import Card from './ui/Card';
import Button from './ui/Button';
import { PhraseExplanation, resumeAPI } from '../lib/api';
import { Brain, Target, TrendingUp, AlertTriangle, Lightbulb } from 'lucide-react';

interface ExplainableAnalysisProps {
  matchScore: number;
  explanations: PhraseExplanation[];
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  resumeText: string;
  uploadedFile?: File;
}

export const ExplainableAnalysis: React.FC<ExplainableAnalysisProps> = ({
  matchScore = 0,
  explanations = [],
  summary = '',
  strengths = [],
  weaknesses = [],
  suggestions = [],
  resumeText = '',
  uploadedFile
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [hoveredPhrase, setHoveredPhrase] = useState<string | null>(null);
  const [annotatedPdfUrl, setAnnotatedPdfUrl] = useState<string | null>(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  // Highlight phrases in resume text
  const highlightPhrases = (text: string) => {
    let highlightedText = text;
    
    (explanations || []).forEach((explanation) => {
      const regex = new RegExp(`(${explanation.phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      const weight = explanation.weight;
      
      let className = '';
      if (weight >= 7) className = 'bg-green-200 border-green-500';
      else if (weight >= 4) className = 'bg-blue-200 border-blue-500';
      else if (weight >= 0) className = 'bg-yellow-200 border-yellow-500';
      else if (weight >= -3) className = 'bg-orange-200 border-orange-500';
      else className = 'bg-red-200 border-red-500';
      
      highlightedText = highlightedText.replace(regex, 
        `<span class="highlight-phrase ${className} border px-1 rounded cursor-pointer" 
         data-phrase="${explanation.phrase}" 
         data-weight="${weight}" 
         data-justification="${explanation.justification}"
         data-category="${explanation.category}">$1</span>`
      );
    });
    
    return highlightedText;
  };

  const getWeightColor = (weight: number) => {
    if (weight >= 7) return 'text-green-600';
    if (weight >= 4) return 'text-blue-600';
    if (weight >= 0) return 'text-yellow-600';
    if (weight >= -3) return 'text-orange-600';
    return 'text-red-600';
  };

  const getWeightLabel = (weight: number) => {
    if (weight >= 7) return 'Very Positive';
    if (weight >= 4) return 'Positive';
    if (weight >= 0) return 'Neutral';
    if (weight >= -3) return 'Negative';
    return 'Very Negative';
  };

  const filteredExplanations = selectedCategory === 'all' 
    ? explanations || []
    : (explanations || []).filter(exp => exp.category === selectedCategory);

  const categories = ['all', ...Array.from(new Set((explanations || []).map(exp => exp.category)))];

  // Generate annotated PDF
  const generateAnnotatedPdf = async () => {
    if (!uploadedFile || explanations.length === 0) return;
    
    setIsGeneratingPdf(true);
    try {
      const { annotated_pdf_base64, file_name } = await resumeAPI.createAnnotatedPDF(uploadedFile, explanations);
      const pdfBlob = new Blob([Uint8Array.from(atob(annotated_pdf_base64), c => c.charCodeAt(0))], { type: 'application/pdf' });
      const pdfUrl = URL.createObjectURL(pdfBlob);
      setAnnotatedPdfUrl(pdfUrl);
    } catch (error) {
      console.error('Error generating annotated PDF:', error);
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Match Score */}
      <Card>
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">AI Match Analysis</h3>
          <div className="flex items-center justify-center space-x-4">
            <div className="text-6xl font-bold text-primary-600">{matchScore}%</div>
            <div className="text-left">
              <p className="text-sm text-gray-600">Match Score</p>
              <p className="text-xs text-gray-500">AI-powered analysis</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Summary */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Brain className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Analysis Summary</h3>
        </div>
        <p className="text-gray-700 leading-relaxed">{summary}</p>
      </Card>

      {/* Category Filter */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Target className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filter by Category</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
            </Button>
          ))}
        </div>
      </Card>

      {/* Phrase Explanations */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Detailed Explanations</h3>
        </div>
        <div className="space-y-4">
          {filteredExplanations.map((explanation, index) => (
            <div
              key={index}
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              onMouseEnter={() => setHoveredPhrase(explanation.phrase)}
              onMouseLeave={() => setHoveredPhrase(null)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm font-medium text-gray-600">
                      {explanation.category.charAt(0).toUpperCase() + explanation.category.slice(1)}
                    </span>
                    <span className={`text-sm font-bold ${getWeightColor(explanation.weight)}`}>
                      {explanation.weight > 0 ? '+' : ''}{explanation.weight}/10
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${getWeightColor(explanation.weight)} bg-opacity-20`}>
                      {getWeightLabel(explanation.weight)}
                    </span>
                  </div>
                  <p className="text-gray-900 font-medium mb-2">"{explanation.phrase}"</p>
                  <p className="text-gray-600 text-sm">{explanation.justification}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Strengths and Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="w-5 h-5 text-success-600" />
            <h3 className="text-lg font-semibold text-gray-900">Strengths</h3>
          </div>
          <ul className="space-y-2">
            {strengths.map((strength, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-success-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-warning-600" />
            <h3 className="text-lg font-semibold text-gray-900">Areas for Improvement</h3>
          </div>
          <ul className="space-y-2">
            {weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-warning-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-gray-700">{weakness}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Suggestions */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb className="w-5 h-5 text-warning-600" />
          <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
        </div>
        <ul className="space-y-2">
          {suggestions.map((suggestion, index) => (
            <li key={index} className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-warning-500 rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-gray-700">{suggestion}</span>
            </li>
          ))}
        </ul>
      </Card>

      {/* Annotated PDF Display */}
      {uploadedFile && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Annotated PDF</h3>
            <Button
              onClick={generateAnnotatedPdf}
              disabled={isGeneratingPdf || explanations.length === 0}
              variant="primary"
              size="sm"
            >
              {isGeneratingPdf ? 'Generating...' : 'Generate Annotated PDF'}
            </Button>
          </div>
          
          {annotatedPdfUrl && (
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">PDF with AI Annotations</h4>
                <p className="text-xs text-gray-600 mb-3">
                  This PDF shows your resume with highlighted phrases and detailed explanations of how each phrase impacts your match score.
                </p>
                <div className="flex space-x-2">
                  <Button
                    onClick={() => window.open(annotatedPdfUrl, '_blank')}
                    variant="secondary"
                    size="sm"
                  >
                    View PDF
                  </Button>
                  <Button
                    onClick={() => {
                      const link = document.createElement('a');
                      link.href = annotatedPdfUrl;
                      link.download = 'annotated_resume.pdf';
                      link.click();
                    }}
                    variant="secondary"
                    size="sm"
                  >
                    Download PDF
                  </Button>
                </div>
              </div>
              
              <div className="text-xs text-gray-500">
                <p><strong>PDF Features:</strong></p>
                <ul className="mt-2 space-y-1">
                  <li>• Green highlights: Strong positive matches</li>
                  <li>• Red highlights: Areas for improvement</li>
                  <li>• Weight indicators: 🟢 High impact, 🟡 Medium, 🔴 Low</li>
                  <li>• Bubble annotations: Detailed explanations</li>
                  <li>• Summary page: Analysis overview</li>
                </ul>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Highlighted Resume Text */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resume with AI Highlights</h3>
        <div 
          className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto"
          dangerouslySetInnerHTML={{ __html: highlightPhrases(resumeText) }}
        />
        <div className="mt-4 text-xs text-gray-500">
          <p><strong>Legend:</strong></p>
          <div className="flex flex-wrap gap-2 mt-2">
            <span className="bg-green-200 border-green-500 border px-2 rounded">Very Positive (+7-10)</span>
            <span className="bg-blue-200 border-blue-500 border px-2 rounded">Positive (+4-6)</span>
            <span className="bg-yellow-200 border-yellow-500 border px-2 rounded">Neutral (0-3)</span>
            <span className="bg-orange-200 border-orange-500 border px-2 rounded">Negative (-1 to -3)</span>
            <span className="bg-red-200 border-red-500 border px-2 rounded">Very Negative (-4 to -10)</span>
          </div>
        </div>
      </Card>
    </div>
  );
}; 